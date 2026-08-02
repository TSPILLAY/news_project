# News Management System

A multi-role news management platform and RESTful API built with Django, Django REST Framework, and MariaDB/MySQL. The system features role-based access control (Readers, Journalists, Editors, Administrators), article review and approval workflows, curated newsletters, automated email notifications, and subscription-filtered REST API endpoints.

---

## 🚀 Features & User Roles

* **Reader:** Browse approved news feeds, view curated newsletters, and subscribe to favorite publishers or independent journalists.
* **Journalist:** Draft and submit news articles for editor review, edit/delete authored content, and curate custom newsletters.
* **Editor:** Review pending submissions via an editor dashboard, approve/publish articles, and manage news output.
* **Administrator:** Full database and user permission management via the Django Admin interface.
* **Automated Signals:** Post-save signals dispatch email notifications to subscribers upon article approval and send webhook payloads to external logging services.
* **REST API:** Role-restricted endpoints for article listing and personalized subscription feeds.

---

## 📖 How to Use the Application

### 1. Account Registration & Authentication
* Navigate to `/register/` to create a new account.
* Select your desired role during registration: **Reader**, **Journalist**, or **Editor**.
* Use `/login/` and `/logout/` to manage your active session. The navigation bar updates dynamically based on your role.

### 2. Reader Workflows
* **Home Feed (`/`):** View all editor-approved news articles sorted by release date.
* **Newsletters (`/newsletters/`):** Browse curated newsletters compiled by journalists and editors.
* **API Feed (`/api/articles/subscribed/`):** View personalized article feeds filtered by your publisher and journalist subscriptions.

### 3. Journalist Workflows
* **Submit Articles (`/articles/create/`):** Submit new articles. Articles remain in a `pending` state until reviewed by an editor.
* **Manage Articles:** View your published articles on the main feed and use the **Edit** and **Delete** options on your authored posts. *(Note: Editing an article resets its approval status to pending for re-review).*
* **Curate Newsletters (`/newsletters/create/`):** Create custom newsletters containing selected published articles. You can also edit or delete your existing newsletters from the newsletter view.

### 4. Editor Workflows
* **Editor Dashboard (`/pending/`):** View a dedicated queue of all articles awaiting approval.
* **Approve & Publish (`/approve/<article_id>/`):** Review article content and click **Approve & Publish** to instantly publish the article to the public home feed and trigger subscriber notifications.

### 5. Administrator Workflows
* Access `/admin/` with your superuser credentials to manage users, assign roles, inspect database tables, and configure system models directly.

---

## 📋 Prerequisites

Ensure you have the following installed on your system before proceeding:

* **Python** (v3.10 or higher)
* **Git**
* **MariaDB** or **MySQL Server** (running locally on default port `3306`)
* **Docker & Docker Compose** *(Optional, for containerized environments)*

---

## 🛠️ Step-by-Step Setup Guide

### 1. Clone the Repository
Open your terminal and clone the repository:
```bash
git clone [https://github.com/TSPILLAY/news_project.git](https://github.com/TSPILLAY/news_project.git)
cd news_project