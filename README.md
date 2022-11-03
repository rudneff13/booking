# Booking project test task

For this assignment, the Django framework and Postgresql database are used.
The project is containerized within docker-compose.
Most project configs are stored in "/env/.env.development" file 
(it shouldn't be stored in git in production but for exercise purposes it is).

Assignment logic is implemented within the "rent" application.

## Fast-start
Run containers one by one to prevent starting the web server before the database
(can be resolved with the famous "wait-for-it" script but let's skip this step).

<br>

Build project:
> * docker-compose build

Start postgres db:
> * docker-compose up -d db

Start django web server:
> * docker-compose up -d web

Run tests:
> * docker-compose exec web python manage.py test

Generate coverage report (or just run a script "./cvrg"):
> * docker-compose exec web coverage erase
> * docker-compose exec web coverage run manage.py test
> * docker-compose exec web coverage report

When you finish work with the project run:
> * docker-compose down


## The available endpoints:
* Django admin: http://0.0.0.0:8000/admin/
* Django swagger: http://0.0.0.0:8000/swagger/

* Rentals create/list:            http://0.0.0.0:8000/rentals/
* Rentals get/delete:             http://0.0.0.0:8000/rentals/{id}
* Reservations create/list:       http://0.0.0.0:8000/reservations/
* Reservations get/delete/put:    http://0.0.0.0:8000/reservations/{id}

All required information regarding the endpoints usage can be found in swagger

Code coverage is over 90%.
