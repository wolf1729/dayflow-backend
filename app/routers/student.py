from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import Response
from bson import ObjectId
from pymongo import ReturnDocument

from app.models.student import StudentModel, UpdateStudentModel, StudentCollection
from app.core.database import db

router = APIRouter(prefix="/students", tags=["students"])
student_collection = db.get_collection("students")

@router.post(
    "/",
    response_description="Add new student",
    response_model=StudentModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_student(student: StudentModel = Body(...)):
    new_student = student.model_dump(by_alias=True, exclude=["id"])
    result = await student_collection.insert_one(new_student)
    new_student["_id"] = result.inserted_id
    return new_student

@router.get(
    "/",
    response_description="List all students",
    response_model=StudentCollection,
    response_model_by_alias=False,
)
async def list_students():
    return StudentCollection(students=await student_collection.find().to_list(1000))

@router.get(
    "/{id}",
    response_description="Get a single student",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def show_student(id: str):
    if (student := await student_collection.find_one({"_id": ObjectId(id)})) is not None:
        return student
    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@router.put(
    "/{id}",
    response_description="Update a student",
    response_model=StudentModel,
    response_model_by_alias=False,
)
async def update_student(id: str, student: UpdateStudentModel = Body(...)):
    student_dict = {
        k: v for k, v in student.model_dump(by_alias=True).items() if v is not None
    }

    if len(student_dict) >= 1:
        update_result = await student_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": student_dict},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Student {id} not found")

    if (existing_student := await student_collection.find_one({"_id": ObjectId(id)})) is not None:
        return existing_student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@router.delete("/{id}", response_description="Delete a student")
async def delete_student(id: str):
    delete_result = await student_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")
