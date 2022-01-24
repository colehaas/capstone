# Introduction 
The Driver Incentive Program -- DriveRite (by DriveRite Technologies) is a Django-based web application designed to empower transportation companies to give points to their drivers, and 
allow those drivers to pick rewards from a sponsor-curated set of online-shoppable items.

# Build and Test Locally

1.	pip install -r requirements.txt --user
2.	python manage.py makemigrations
3.	python manage.py migrate
4.  python manage.py createsuperuser
        **Creating superuser is crucial if this code is run locally with a from-scratch DB
        - Log into [base-url]/admin with the new superuser
        - Add a UserInformation Record, connect to your superuser User account, add Role 'admin', check "IsAdmin" bool
        - With this initial admin account, all other user management can be done from frontend
5.	python manage.py runserver

# Contribute

1.	git add --all
2.	git commit -m "message"
3.	git push
4.  Navigate to Azure DevOps ; specifically the Repos/Branches section
5.  Create a Pull Request for your new branch, and double check your changes
6.  Complete the Pull Request (this updates Main)
7.  Sync your local Main branch, then delete your development branch
