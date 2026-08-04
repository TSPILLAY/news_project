# News Management System

A multi-role news management platform and RESTful API built with Django, Django REST Framework, and MariaDB/MySQL. The system features role-based access control (Readers, Journalists, Editors, Administrators), article review and approval workflows, curated newsletters, automated email notifications, and subscription-filtered REST API endpoints[cite: 11].

---

## 🚀 Features & User Roles

* **Reader:** Browse approved news feeds, view curated newsletters, manage publisher and journalist subscriptions, and access custom API feeds[cite: 11].
* **Journalist:** Draft and submit news articles for editor review, edit/delete authored content (both pre and post approval), and curate custom newsletters[cite: 11].
* **Editor:** Review pending submissions via an editor dashboard, approve/publish articles, edit or delete any article/newsletter, and manage publisher organizations and staff[cite: 11].
* **Administrator:** Full database and user permission management via the Django Admin interface[cite: 11].
* **Automated Signals:** Post-save signals dispatch email notifications to subscribers upon article approval and send webhook payloads to external logging services[cite: 11].
* **REST API:** Role-restricted endpoints for article listing and personalized subscription feeds[cite: 11].

---

## 📖 How to Use the Application

### 1. Account Registration & Authentication
* Navigate to `/register/` to create a new account[cite: 11].
* Select your desired role during registration: **Reader**, **Journalist**, or **Editor**[cite: 11].
* Use `/login/` and `/logout/` to manage your active session[cite: 11]. The system redirects users to the home feed upon successful authentication.

### 2. Reader Workflows
* **Home Feed (`/`):** View all editor-approved news articles sorted by release date[cite: 11].
* **Subscriptions (`/subscriptions/`):** Dedicated page for readers to select and manage their publisher and journalist subscriptions.
* **Newsletters (`/newsletters/`):** Browse curated newsletters compiled by journalists and editors[cite: 11].
* **API Feed (`/api/articles/subscribed/`):** View personalized article feeds filtered by your publisher and journalist subscriptions[cite: 11].

### 3. Journalist Workflows
* **Submit Articles (`/articles/create/`):** Submit new articles[cite: 11]. Articles remain in a `pending` state until reviewed by an editor[cite: 11].
* **Manage Articles:** View your published articles on the main feed and use the **Edit** and **Delete** options on your authored posts regardless of whether they have been approved yet[cite: 11]. *(Note: Editing an article resets its approval status to pending for re-review)*[cite: 11].
* **Curate Newsletters (`/newsletters/create/`):** Create custom newsletters containing selected published articles[cite: 11]. You can also edit or delete your existing newsletters[cite: 11].

### 4. Editor Workflows
* **Editor Dashboard (`/pending/`):** View a dedicated queue of all articles awaiting approval[cite: 11].
* **Approve & Publish (`/approve/<article_id>/`):** Review article content and click **Approve & Publish** to instantly publish the article to the public home feed and trigger subscriber notifications[cite: 11].
* **Manage Publishers (`/publishers/manage/`):** Dedicated dashboard to create publishers and assign editors and journalists to them.
* **Global Content Moderation:** Edit or delete any article or newsletter across the platform.

### 5. Administrator Workflows
* Access `/admin/` with your superuser credentials to manage users, assign roles, inspect database tables, and configure system models directly[cite: 11].

---

## 📋 Prerequisites

Ensure you have the following installed on your system before proceeding:

* **Python** (v3.10 or higher)[cite: 11]
* **Git**[cite: 11]
* **MariaDB** or **MySQL Server** (running locally on default port `3306`)[cite: 11]

---

## 🛠️ Step-by-Step Setup Guide

### 1. Clone the Repository
Open your terminal and clone the repository[cite: 11]:
```bash
git clone [https://github.com/TSPILLAY/news_project.git](https://github.com/TSPILLAY/news_project.git)
cd news_project
