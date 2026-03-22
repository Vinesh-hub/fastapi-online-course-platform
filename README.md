
# 🎓 Online Course Platform API

A robust RESTful API built with **FastAPI** to manage a learning ecosystem. This platform handles course discovery, intelligent enrollment fee calculations, and a persistent student wishlist system.

## 🚀 Features

* **Course Management**: Browse available courses with real-time seat tracking.
* **Smart Enrollments**: 
    * Dynamic fee calculation (Early Bird & Coupon discounts).
    * Support for "Gift Enrollments" with recipient validation.
    * Automatic seat decrementing upon successful signup.
* **Wishlist System**:
    * Add/Remove courses for specific students.
    * Duplicate prevention (Student + Course ID combo).
    * **Bulk Enrollment**: One-click "Enroll-All" feature that processes an entire wishlist, checks seat availability, and clears the cart.
* **Advanced Filtering**: Filter courses by category or availability (sold out vs. available).

## 🛠️ Tech Stack

* **Framework**: FastAPI
* **Server**: Uvicorn
* **Data Validation**: Pydantic
* **Language**: Python 3.9+
