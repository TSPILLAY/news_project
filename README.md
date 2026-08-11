# News Application

A Django-based news application that allows readers to view approved articles and newsletters, journalists to create and manage their own content, and editors to review, approve, edit, and delete articles.

The application includes role-based access control, newsletter management, article subscriptions, a RESTful API, JWT authentication, automated tests, and email/API notifications when articles are approved.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [User Roles](#user-roles)
* [Article Workflow](#article-workflow)
* [Newsletter Workflow](#newsletter-workflow)
* [Project Structure](#project-structure)
* [Requirements](#requirements)
* [Installation](#installation)
* [Database Configuration](#database-configuration)
* [Running the Application](#running-the-application)
* [Creating an Administrator](#creating-an-administrator)
* [User Registration](#user-registration)
* [REST API](#rest-api)
* [API Authentication](#api-authentication)
* [API Permissions](#api-permissions)
* [Automated Testing](#automated-testing)
* [Article Approval Notifications](#article-approval-notifications)
* [Security](#security)
* [Troubleshooting](#troubleshooting)
* [Conclusion](#conclusion)

---

## Project Overview

This project is a Django-based news platform designed to support publishers, independent journalists, editors, and readers.

The application allows:

* Journalists to create and manage articles.
* Journalists to create newsletters.
* Editors to review and approve articles.
* Editors to edit or delete articles before and after approval.
* Readers to view approved articles and newsletters.
* Readers to subscribe to publishers and journalists.
* Newsletters to contain only approved articles.
* Approved articles to trigger subscriber notifications.
* Third-party applications to access articles through a RESTful API.

The application uses Django for the web application, Django REST Framework for the API, JWT authentication for API access, and MariaDB/MySQL for database storage.

---

## Features

### Article Management

The application supports:

* Creating articles.
* Viewing articles.
* Editing articles.
* Deleting articles.
* Approving articles.
* Publishing approved articles.
* Tracking article approval status.
* Associating articles with journalists and publishers.

Journalists can view their own articles even when they have not yet been approved. This allows journalists to make changes or withdraw an article while it is still awaiting editorial review.

Editors can manage articles throughout the entire lifecycle, including both pending and approved articles.

---

### Newsletter Management

The application allows journalists and editors to create and manage newsletters.

Newsletters contain:

* Title
* Description
* Author
* Creation date
* Articles

Only **approved articles** can be selected when creating or editing a newsletter. This prevents an unapproved article from bypassing the editorial approval process.

---

### User Management

The application uses a custom Django user model.

Users can have one of the following roles:

* Reader
* Journalist
* Editor

Registration email addresses are required to be unique to prevent duplicate accounts and subscription notification issues.

---

### Subscription Management

Readers can subscribe to:

* Publishers
* Journalists

The subscribed article API allows a reader to retrieve approved articles from the publishers and journalists they follow.

---

### RESTful API

The project provides a RESTful API for accessing articles and related resources.

The API uses Django REST Framework and JWT authentication.

Supported API functionality includes:

* Retrieve approved articles.
* Retrieve a single article.
* Retrieve articles from subscribed publishers and journalists.
* Create articles.
* Update articles.
* Delete articles.
* Approve articles.
* Retrieve publishers.
* Retrieve users.
* Retrieve newsletters.

---

## User Roles

### Reader

Readers can:

* View approved articles.
* View newsletters.
* Subscribe to publishers.
* Subscribe to journalists.
* Retrieve articles from their subscriptions through the API.

Readers cannot:

* Create articles.
* Edit articles.
* Delete articles.
* Approve articles.

---

### Journalist

Journalists can:

* Create articles.
* View their own articles.
* View pending articles they have created.
* Edit their own articles.
* Delete their own articles.
* Create newsletters.
* Edit newsletters.
* Delete newsletters.
* View approved articles.

When a journalist edits an already approved article, the article is returned to the pending approval state so that it can be reviewed again by an editor.

---

### Editor

Editors have content moderation permissions.

Editors can:

* View pending articles.
* View approved articles.
* Approve articles.
* Edit pending articles.
* Delete pending articles.
* Edit approved articles.
* Delete approved articles.
* Create newsletters.
* Edit newsletters.
* Delete newsletters.

This allows editors to manage articles both before and after publication.

---

## Article Workflow

The article approval workflow is:

```text
Journalist creates article
        |
        v
Article is Pending
        |
        +----------------------+
        |                      |
        v                      v
Journalist edits          Journalist deletes
article if required       article if required
        |
        v
Editor reviews article
        |
        +----------------------+
        |                      |
        v                      v
Editor edits             Editor deletes
article                  article
        |
        v
Editor approves article
        |
        v
Article becomes Approved
        |
        v
Article is Published
        |
        +----------------------+
        |                      |
        v                      v
Subscribers receive      Article can be edited
notification             or deleted by editor
```

An article is not available for newsletter selection until it has been approved.

---

## Newsletter Workflow

The newsletter workflow is:

```text
Journalist/Editor creates newsletter
        |
        v
Select approved articles
        |
        v
Save newsletter
        |
        v
Readers can view newsletter
```

Only articles where:

```text
approved = True
```

can be selected for a newsletter.

This ensures that the newsletter system cannot be used to publish an article before it has passed editorial approval.

---

## Project Structure

The main project structure is:

```text
news_project/
│
├── manage.py
│
├── news_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── news_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
│
├── templates/
│   └── news_app/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── article_list.html
│       ├── my_articles.html
│       ├── create_article.html
│       ├── edit_article.html
│       ├── delete_article_confirm.html
│       ├── approve_articles.html
│       ├── create_newsletter.html
│       ├── edit_newsletter.html
│       └── newsletter_list.html
│
├── requirements.txt
└── README.md
```

---

## Requirements

The project requires:

* Python 3.x
* Django
* Django REST Framework
* Django REST Framework Simple JWT
* MariaDB or MySQL
* MySQL Python database connector
* Requests

The exact Python packages are listed in:

```text
requirements.txt
```

---

# Installation

## 1. Clone the Repository

Open a terminal and clone the project:

```bash
git clone https://github.com/TSPILLAY/news_project.git
cd news_project
```

---

## 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

### Windows

Activate the environment with:

```bash
venv\Scripts\activate
```

### macOS/Linux

Activate the environment with:

```bash
source venv/bin/activate
```

After activation, the terminal should indicate that the virtual environment is active.

---

## 3. Install Dependencies

Install the project's required packages:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, the main packages required by the application include:

```bash
pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install requests
pip install mysqlclient
```

---

# Database Configuration

This project uses MariaDB/MySQL as its database.

Make sure MariaDB/MySQL is installed and running before starting the application.

Create a database for the project.

For example:

```sql
CREATE DATABASE news_db;
```

The database configuration is located in:

```text
news_project/settings.py
```

The configuration should contain the appropriate:

* Database name
* Username
* Password
* Host
* Port

Example:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'news_db',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

For security, real database passwords should not be committed to GitHub.

Environment variables are recommended for production or shared repositories.

---

# Run Database Migrations

After configuring the database, create and apply the migrations.

Run:

```bash
python manage.py makemigrations
```

Then:

```bash
python manage.py migrate
```

This creates the database tables required by Django and the news application.

---

# Creating an Administrator

Create a Django superuser using:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:

* Username
* Email address
* Password

The administrator can then access the Django admin interface.

---

# Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

The application will normally be available at:

```text
http://127.0.0.1:8000/
```

Open the address in a web browser.

---

# User Registration

Users can register through the registration page.

The registration process requires a unique email address.

Example:

```text
/register/
```

Available roles include:

* Reader
* Journalist
* Editor

The application validates the email address during registration to prevent duplicate accounts.

---

# Article Management

## Journalist

A journalist can create an article through the article creation page.

A newly created article is initially pending approval.

The journalist can access their own articles through:

```text
/articles/mine/
```

The journalist can:

* View pending articles.
* Edit articles.
* Delete articles.
* View approval status.

---

## Editor

The editor dashboard contains two sections:

### Pending Articles

Pending articles can be:

* Approved and published.
* Edited.
* Deleted.

### Approved Articles

Approved articles can be:

* Viewed.
* Edited.
* Deleted.

This ensures editors have control over content before and after publication.

---

# REST API

The project includes a RESTful API built using Django REST Framework.

The API allows authorised clients to interact with article, publisher, user, and newsletter data.

## Article Endpoints

### Retrieve Approved Articles

```http
GET /api/articles/
```

Returns a list of approved articles.

---

### Retrieve Subscribed Articles

```http
GET /api/articles/subscribed/
```

Returns approved articles from the publishers and journalists that the authenticated reader follows.

---

### Retrieve a Single Article

```http
GET /api/articles/<id>/
```

Returns a single article.

---

### Create an Article

```http
POST /api/articles/
```

Creating an article is restricted to journalists.

Example request:

```json
{
    "title": "Example Article",
    "content": "This is the content of the article.",
    "publisher": null
}
```

New articles require editorial approval before publication.

---

### Update an Article

```http
PUT /api/articles/<id>/
```

Articles can be updated by authorised journalists and editors.

---

### Delete an Article

```http
DELETE /api/articles/<id>/
```

Articles can be deleted by authorised journalists and editors.

---

### Approve an Article

```http
POST /api/articles/<id>/approve/
```

Article approval is restricted to editors.

---

# API Authentication

The API uses JWT token-based authentication through Django REST Framework Simple JWT.

The token endpoints are:

```text
/api/token/
/api/token/refresh/
```

## Obtain a Token

Send a POST request to:

```http
POST /api/token/
```

with:

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

A successful request returns an access token and refresh token.

Example:

```json
{
    "refresh": "your_refresh_token",
    "access": "your_access_token"
}
```

The access token should be included in authenticated API requests.

Use the following HTTP header:

```text
Authorization: Bearer your_access_token
```

---

## Refresh a Token

When an access token expires, use:

```http
POST /api/token/refresh/
```

Example:

```json
{
    "refresh": "your_refresh_token"
}
```

---

# API Permissions

The API uses role-based authorization.

| Operation                | Reader | Journalist | Editor |
| ------------------------ | -----: | ---------: | -----: |
| View approved articles   |    Yes |        Yes |    Yes |
| View subscribed articles |    Yes |         No |     No |
| Create article           |     No |        Yes |     No |
| Update article           |     No |        Yes |    Yes |
| Delete article           |     No |        Yes |    Yes |
| Approve article          |     No |         No |    Yes |

Readers are restricted to viewing content.

Journalists can create and manage their own articles.

Editors have moderation privileges and can approve, edit, and delete articles.

---

# Serializers

The project uses Django REST Framework serializers for the main application models.

Serializers are provided for:

* User
* Publisher
* Article
* Newsletter

These serializers control how model data is converted to and from JSON when interacting with the REST API.

---

# Article Approval Notifications

The project uses Django Signals to perform additional actions when an article is approved.

When an article changes from unapproved to approved:

1. The approval is detected.
2. Subscribers are identified.
3. An email notification is sent to relevant subscribers.
4. A POST request is made to the project's approved-article API logging endpoint.

This simulates sharing approved content externally while keeping the integration within the project.

---

# Newsletter Restrictions

Only approved articles can be added to newsletters.

This restriction is implemented in the newsletter form by filtering the available articles to approved content.

This prevents the following situation:

```text
Unapproved Article
       |
       v
Newsletter
       |
       v
Reader sees article
```

Instead, the required workflow is:

```text
Unapproved Article
       |
       v
Editor Approval
       |
       v
Approved Article
       |
       v
Newsletter
       |
       v
Reader
```

---

# Automated Testing

The project includes automated tests using Django's testing framework.

Run the complete test suite with:

```bash
python manage.py test
```

The tests cover functionality including:

* User registration.
* Duplicate email validation.
* Role-based access.
* Journalist article visibility.
* Pending articles.
* Newsletter article filtering.
* Editor article access.
* Article management.

The tests include both successful and unsuccessful scenarios where applicable.

---

# Example API Testing

The API can be tested using tools such as:

* Postman
* Insomnia
* Django's automated testing framework
* Browser/API clients

Example authentication request:

```http
POST /api/token/
```

Example article request:

```http
GET /api/articles/
```

Example subscribed article request:

```http
GET /api/articles/subscribed/
Authorization: Bearer <access_token>
```

---

# Error Handling and Defensive Coding

The application uses validation and defensive coding techniques to reduce errors caused by invalid input.

Examples include:

* Unique email validation.
* Form validation.
* Authentication checks.
* Role-based access checks.
* Handling missing articles using Django's `get_object_or_404`.
* Restricting newsletter selection to approved articles.
* Restricting API actions based on user roles.
* Validation of user input.
* Exception handling for external API requests.

---

# Security

The application uses several security mechanisms, including:

* Django authentication.
* JWT authentication for the REST API.
* Role-based access control.
* Django permissions.
* CSRF protection through Django forms.
* Login-required views.
* Restricted editor and journalist functionality.
* Unique user email addresses.

Sensitive information such as database passwords and secret keys should not be committed to the repository.

For a production deployment, environment variables should be used for sensitive configuration.

---

# Troubleshooting

## Database Connection Error

If Django cannot connect to MariaDB/MySQL:

1. Confirm that the database server is running.
2. Confirm that the database exists.
3. Check the database username.
4. Check the database password.
5. Check the host and port in `settings.py`.

---

## Migration Error

Try:

```bash
python manage.py makemigrations
python manage.py migrate
```

If there are existing migration problems, review the migration files and database state before deleting or recreating migrations.

---

## Server Will Not Start

Make sure the virtual environment is activated:

### Windows

```bash
venv\Scripts\activate
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

Finally run:

```bash
python manage.py runserver
```

---

## API Authentication Error

If an API request returns an authentication error:

1. Obtain a JWT token using `/api/token/`.
2. Copy the access token.
3. Add the token to the request header.

Example:

```text
Authorization: Bearer <access_token>
```

Ensure the token has not expired.

---

# Development Workflow

A typical development workflow is:

```text
Clone repository
      |
      v
Create virtual environment
      |
      v
Install dependencies
      |
      v
Configure database
      |
      v
Run migrations
      |
      v
Create superuser
      |
      v
Run development server
      |
      v
Register/login users
      |
      v
Create articles
      |
      v
Review articles as editor
      |
      v
Approve articles
      |
      v
Create newsletters
      |
      v
Test REST API
      |
      v
Run automated tests
```

---

# Conclusion

The News Application provides a complete workflow for creating, reviewing, approving, publishing, and consuming news content.

The application demonstrates:

* Django web development.
* Custom user models.
* Role-based access control.
* Article management.
* Editorial approval workflows.
* Newsletter management.
* Publisher and journalist subscriptions.
* Django Signals.
* Email notifications.
* RESTful API development.
* JWT authentication.
* Automated testing.
* Defensive programming.
* Database integration.

The application is designed to ensure that unpublished content cannot bypass the editorial approval process while still allowing journalists and editors to manage content appropriately.
