# Studydeck Forum
This is my submission for a forum type site for the recruitment task for SUTT

---
## Features

### Authentication:
- Google OAuth (restricted to @pilani.bits-pilani.ac.in)
- Takes username and generates profile all from Google Sign-in
- Role-based access (User & Moderator)
- For **ADMIN** access:
  - Username: ```admin```
  - Password:```admin```

### Some Basic Models:
- Courses (are populated automatically by management command)
- Resources
- Users/Profiles

### Forum Core:
- Categories & Threads
- Threads are optionally linked with courses
- Posting & Reply with markdown support
- Thread locking & deletion
- Liking/upvote system for threads & replies
- Reporting system with moderator resolution (can delete or mark safe)
- Threads sorting (latest / likes)
- Pagination (10 threads & replies per page)
- Mention system for threads & replies (using `re`)
   
### Discovery:
- Tags with their dedicated pages
- Course-wise thread pages
- Fuzzy search globally using PostgreSQL ```pg_trgm```
- Search also fallbacks to ```icontains```

### Moderation:
- Report lists (only for moderators)
- Soft deletes
- Moderators can bypass perms to delete any reply/thread

### Email Notification:
- Mention & reply notifications are implemented and emails are sent within console.
- **SMTP is disabled on the deployed demo** cause of unavailability on free-tier hosting.

---
## Setup Instruction
```
git clone <repo-url>
cd Studydeck-forum
python -m venv venv  
source venv/bin/activate
pip install -r requirements.txt
cd SDForum
python manage.py migrate
python manage.py populate_courses
python manage.py runserver
```
---
## Deployment Notes
- PostgreSQL is used in production
- Migrations + course population run during deploy
- Admin user created via environment-based command

---
## Design Decisions

### Users & Courses models:
- `Profile` model is used for role and user assignment (used django native AUTH_USER_MODEL)
- Made `Course` model with necessary properties and a unique slug
- `Resource` model has its types ("PDF","VIDEO",LINK") and a link attached to it
- Resource model also is attached to the Course model

### Forum models:
- Category: Has own unique slug
- Threads & Replies:
  - Has foreign referential with Category, Author(User), Tags, Course Models
  - Has own is_deleted field for soft deletes
- Tags:
  - Has unique slug for linking in Tag-lists
  - Used by thread models with `ManyToManyField` for multiple tags addition
- Likes:
  - Likes are reffered to User and Thread/Reply models
- Report:
  - Reports reference either a Thread/Reply and the reporter(User)
  - Status-based resolution (`PENDING`, `RESOLVED`)
- Mentions:
  - Mentions are reffered to Thread/Reply and the mentioned user (for email sending)
---
