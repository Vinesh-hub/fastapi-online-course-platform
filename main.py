from fastapi import FastAPI,Query,Response,status
from pydantic import BaseModel,Field

app=FastAPI()

#Pydantic Models

class EnrollRequest(BaseModel):
    student_name:     str=Field(...,min_length=2)
    course_id:        int=Field(...,gt=0)
    email:            str=Field(...,min_length=5)
    payment_method:   str=Field("card",description="method of payment")
    coupon_code:      str=Field('\\')
    gift_enrollment:  bool=Field(False)
    recipient_name:   str=Field('\\')


class NewCourse(BaseModel):
    title:str=Query(...,min_length=2)
    instructor:str=Query(...,min_length=2)
    category:str=Query(...,min_length=2)
    level:str=Query(...,min_length=2)
    price:int=Query(...,ge=0)
    seats_left:int=Query(...,gt=0)

class CheckoutRequest(BaseModel):
    student_name:str
    payment_method:str

#Helper Functions
def find_enrolled(course_name):
    course=next((c for c in enrollments if c['course_title']==course_name),None)
    return course
def find_course(course_id):
    course=next((c for c in courses if c['id']==course_id),None)
    return course
def calculate_enrollment_fee(price,seats_left,coupon_code):
    applied_discounts = []
    if seats_left>5:
        price-=(price*0.10)
        applied_discounts.append("Early Bird (10%)")
    if coupon_code=='STUDENT20':
        price-=(price*0.20)
        applied_discounts.append("Student Promo (20%)")
    if coupon_code=='FLAT500':
        price-=500
        applied_discounts.append("Flat 500 Discount")
    return {
        "final_fee":max(0,price),
        'applied_discounts':applied_discounts
    }  
def filter_courses_logic(category=None,level=None,max_price=None,has_seats=None):
        result=courses
        if category is not None:
            result=[c for c in result if c['category'].lower()==category.lower()]
        if level is not None:
            result=[c for c in result if c['level'].lower()==level.lower()]
        if max_price is not None:
            result=[c for c in result if c['price']<=max_price]
        if has_seats is not None:
            result=[c for c in result if (c['seats_left']>0)==has_seats]
        return result
        
 
#Temporary courses list
courses=[
    {"id": 1, "title": "React for Beginners",            "instructor": "Sarah Drasner",      "category": "Web Dev",      "level": "Beginner",     "price": 49, "seats_left": 12},
    {"id": 2, "title": "Advanced Python for Data Science","instructor": "Guido van Rossum", "category": "Data Science",  "level": "Advanced",     "price": 99, "seats_left": 5},
    {"id": 3, "title": "UI/UX Masterclass",              "instructor": "Gary Simon",         "category": "Design",       "level": "Intermediate", "price": 75, "seats_left": 20},
    {"id": 4, "title": "Docker & Kubernetes 101",        "instructor": "Nana Janashia",      "category": "DevOps",       "level": "Beginner",     "price": 60, "seats_left": 8},
    {"id": 5, "title": "Fullstack Next.js",              "instructor": "Lee Robinson",       "category": "Web Dev",      "level": "Advanced",     "price": 0, "seats_left": 15},
    {"id": 6, "title": "Pandas & NumPy Deep Dive",       "instructor": "Wes McKinney",       "category": "Data Science", "level": "Intermediate", "price": 55, "seats_left": 0},
    {"id": 7, "title": "Cloud Native Architecture",      "instructor": "Kelsey Hightower",   "category": "DevOps",       "level": "Advanced",     "price": 150, "seats_left": 3},
    {"id": 8, "title": "Typography and Color Theory",    "instructor": "Ellen Lupton",       "category": "Design",       "level": "Beginner",     "price": 0, "seats_left": 25}
]

enrollments=[]
enrollment_counter=1
wishlist=[]
@app.get('/')
def home():
    return {'messege':"Welcome to LearnHub Online Courses"}


#endpoint to post courses
@app.post('/courses')
def post_courses(new_course:NewCourse,response:Response):
    existing_course=next((c['title'].lower() for c in courses if c['title'].lower()==new_course.title.lower()),None)
    if existing_course:
        response.status_code=status.HTTP_400_BAD_REQUEST
        return {"messege":"course with the name already exists"}
    next_id=max(c['id'] for c in courses)+1
    new_course={
        'id':next_id,
        'title':new_course.title,
        'instructor':new_course.instructor,
        'category':new_course.category,
        'level':new_course.level,
        'price':new_course.price,
        'seats_left':new_course.seats_left
    }
    courses.append(new_course)
    response.status_code=status.HTTP_201_CREATED
    return {"messege":"course added succesfully","course":new_course}


#Endpoint to get courses list
@app.get('/courses')
def get_courses():
    return {
        'courses':courses,
        'total':len(courses),
        'total_seats_available':sum(course['seats_left'] for course in courses)
    }
#End point to get course summery
@app.get('/courses/summery')
def get_summery():
    free_courses=len([course for course in courses if course['price']==0])
    most_expensive_course=max(courses,key=lambda x:x['price'])
    total_seats=sum(course['seats_left'] for course in courses)
    count_by_category={}
    for course in courses:
        category=course['category']
        count_by_category[category]=count_by_category.get(category,0)+1
    return {
        'total_courses':len(courses),
        'free_courses_count':free_courses,
        'most_expensive_course':most_expensive_course,
        'total_seats':total_seats,
        'count_by_category':count_by_category
    }

#End point to filter courses
@app.get('/courses/filter')
def filter_courses(
    category:str=Query(None,descripition="Web Dev,Data Science,DevOps,Design"),
    level:str=Query(None,description="Beginner,Intermediate,Advanced"),
    max_price:int=Query(None,description="Enter maximum price"),
    has_seats:bool=Query(None,description="True or False")
):
    result=filter_courses_logic(category,level,max_price,has_seats)
    return {"filtered_courses":result,"count":len(result)}


#endpoint to search the course by keyword
@app.get('/courses/search')
def search_course(keyword:str=Query(...,min_length=1,description="Enter a keyword to search")):
    results=[c for c in courses if ((keyword.lower() in c['title'].lower()) or (keyword.lower() in c['instructor'].lower()) or (keyword.lower() in c['category'].lower()))]  
    if not results:
        return {"messege":f"No courses found for the {keyword}"}
    return {
        'keyword':keyword,
        'total_found':len(results),
        'results':results
    }

#endpoint to sort
@app.get("/courses/sort")
def sort_courses(
    sort_by:str=Query('price',description='price or title or seats_left'),
    order:str=Query('asc',decription='asc or desc')
):
    if sort_by not in ['price', 'title','seats_left']:
        return {'error': "sort_by must be 'price' or 'title' or 'seats_left"}
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}
    reverse = (order == 'desc')
    sorted_courses = sorted(courses, key=lambda p: p[sort_by], reverse=reverse)
    return {
        'sort_by':  sort_by,
        'order':    order,
        'courses': sorted_courses,
    }

#End point for pagination
@app.get('/courses/page')
def get_course_paged(
    page:int=Query(1,description="enter page number"),
    limit:int=Query(3,description="enter number of courses for page")
):
    start = (page - 1) * limit
    end   = start + limit
    paged = courses[start:end]
    return {
        'page':        page,
        'limit':       limit,
        'total':       len(courses),
        'total_pages': -(-len(courses) // limit),   # ceiling division
        'products':    paged,
    }

#End point for browsing
@app.get('/courses/browse')
def smart_get(
    keyword:str=Query(None,min_length=1,description="Enter a keyword to search"),
    category:str=Query(None),
    level:str=Query(None,description="beginner,intermediate,advanced"),
    max_price:int=Query(None),
    sort_by:str=Query('price',description="price or title or seats_left"),
    order:str=Query('asc',description='asc or desc'),
    page:int=Query(1,description="Enter page"),
    limit:int=Query(3,description="Number of courses for page")
):
    results=courses
    if keyword:
        results=[c for c in results if ((keyword.lower() in c['title'].lower()) or (keyword.lower() in c['instructor'].lower()))]
    if category:
        results=[c for c in results if c["category"].lower()==category.lower()]
    if level:
        results=[c for c in results if c["level"].lower()==level.lower()]
    if max_price is not None:
        results=[c for c in results if c["price"]<=max_price]
    reverse=(order=="desc")
    if sort_by in ["price","title",'seats_left']:
        results=sorted(results,key=lambda x:x[sort_by],reverse=reverse)
    total=len(results)
    start = (page - 1) * limit
    end   = start + limit
    paged = results[start:end]
    return {
        "keyword":keyword,
        'category':category,
        'level':level,
        'max_price':max_price,
        'sort_by':sort_by,
        "order":order,
        'page': page,
        'limit': limit,
        'total_found': len(results),
        'total_pages': -(-total // limit),   # ceiling division
        'courses': paged,
    }

#Endpoint to update the course
@app.put('/courses/{course_id}')
def update_course(
    course_id:int,
    response:Response,
    price:int=Query(None),
    has_seats:int=Query(None)
    ):
    course=find_course(course_id)
    if not course:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"messege":"course not found"}
    if price is not None:
        course['price']=price
    if has_seats is not None:
        course['seats_left']=has_seats
    return {"messege":"updated succesfully","course":course}    
#End point to get course by corse id
@app.get('/courses/{course_id}')
def get_course_by_course_id(course_id:int):
    course=next((c for c in courses if c['id']==course_id),None)
    if course:
        return {"course":course}
    return {"messege":"Course Not Found"}

#Endpoint to delete course
@app.delete('/course/{course_id}')
def delete_course(course_id:int,response:Response):
    course=find_course(course_id)
    if not course:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"messege":"course not found"}
    enroll=find_enrolled(course['title'])
    if enroll:
        return {"messege":"Enrolled course cannot deleted"}
    courses.remove(course)
    return {"messege":f"{course['title']} is deleted"}

#End point to post the enrollments
@app.post('/enrollments')
def post_enrollments(student:EnrollRequest):
    global enrollment_counter
    if student.gift_enrollment and not student.recipient_name.strip():
        return {"Validation error":"recipient name is required for gift Enrollment"}
    course=find_course(student.course_id)
    if not course:
        return {"messege":"course not found"}
    if course['seats_left']==0:
        return {"messege":"Seats are filled"}
    fee=calculate_enrollment_fee(course['price'],course['seats_left'],student.coupon_code)
    course['seats_left']-=1
    enrollment= {
        'enrollment_id':enrollment_counter, 
        'student_name':student.student_name,
        'course_title':course['title'], 
        'instructor':course['instructor'], 
        'original_price':course['price'], 
        'discounts_applied':fee['applied_discounts'], 
        'final_fee':fee['final_fee'],
        'recipient_name':student.recipient_name if student.gift_enrollment else student.student_name
    }
    enrollments.append(enrollment)
    enrollment_counter+= 1
    return {
        "messege":"Succesfully Enrolled",
        "Student":enrollment
    }
    

#End point to get enrollments
@app.get('/enrollments')
def get_enrollments():
    return {
        "enrollments":enrollments,
        'total':len(enrollments)
    }

#endpoint to search the enrollments by student name
@app.get('/enrollments/search')
def search_enrollments(student_name:str=Query(...,min_length=1,description="Enter a student name to search")):
    results=[e for e in enrollments if e['student_name']==student_name]  
    if not results:
        return {"messege":f"No courses found for the {student_name}"}
    return {
        'student_name':student_name,
        'total_found':len(results),
        'results':results
    }

#endpoint to sort enrollments
@app.get("/enrollments/sort")
def sort_enrollments(
    sort_by:str=Query('final_fee'),
    order:str=Query('asc',decription='asc or desc')
):
    if sort_by not in ['final_fee']:
        return {'error': "sort_by must be 'final_fee' "}
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}
    reverse = (order == 'desc')
    sorted_enrollments = sorted(enrollments, key=lambda p: p[sort_by], reverse=reverse)
    return {
        'sort_by':  sort_by,
        'order':    order,
        'enrollments': sorted_enrollments,
    }

#End point for pagination of enrollments
@app.get('/enrollments/page')
def get_enrollments_paged(
    page:int=Query(1,description="enter page number"),
    limit:int=Query(3,description="enter number of courses for page")
):
    start = (page - 1) * limit
    end   = start + limit
    paged = enrollments[start:end]
    return {
        'page':        page,
        'limit':       limit,
        'total':       len(enrollments),
        'total_pages': -(-len(enrollments) // limit),   # ceiling division
        'products':    paged,
    }
#End point get the wishlist
@app.get('/wishlist')
def get_wishlist():
    total=sum(w['price'] for w in wishlist)
    return {
        "wishlist":wishlist,
        "total":total
    }

#End point to add items to the wishlist
@app.post('/wishlist/add')
def add_to_wishlist(
    student_name:str,
    course_id:int
    ):
    course=find_course(course_id)
    if not course:
        return {"messege":"course not found"}
    is_duplicate=any(w for w in wishlist if (w['course_id']==course_id and w['student_name']==student_name))
    if is_duplicate:
        return {"messege":"Already Exists"}
    wishlist_course={
        'student_name':student_name,
        'course_id':course_id,
        'course_title':course['title'],
        'price':course['price']
    }
    wishlist.append(wishlist_course)
    return {
        "course":wishlist_course
    }
    

#End point to remove item from the wishlist
@app.delete('/wishlist/remove/{course_id}')
def delete_item_from_wishlist(
    course_id:int,
    student_name:str
    ):
    course=next((w for w in wishlist if (w['course_id']==course_id and w['student_name']==student_name)),None)
    if course:
        wishlist.remove(course)
        return {"messege":"Removed"}
    return {"messege":"Item not Found in wishlist"}

#End point to enroll the courses in  the wishlist
@app.post('/wishlist/enroll-all')
def enroll_all_from_wishlist(request:CheckoutRequest):
    global enrollment_counter
    student_courses=[course for course in wishlist if course['student_name']==request.student_name]
    if not student_courses:
        return {"messege":"wishlist is empty for the student"}
    confirmations=[]
    total_fee=0
    enrolled_count=0
    for course in student_courses:
        check=find_course(course['course_id'])
        if check and check['seats_left']>0:
            cal=calculate_enrollment_fee(check['price'],check['seats_left'],None)
            fee=cal["final_fee"]
            enrollment_counter+=1
            check['seats_left']-=1
            total_fee+=fee
            enrolled_count+=1
            confirmations.append({
                'enrollment_id':enrollment_counter,
                'course_title':check['title'],
                'fee':fee
            })
            wishlist.remove(course)
    return {
        'student_name':request.student_name,
        'total_enrolled':enrolled_count,
        'grand_total':total_fee
    }
