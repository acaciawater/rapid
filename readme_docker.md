Kenya RAPID for Docker
===============
This Docker setup contains: Kenya RAPID code and postgresql

###Create django.env

> DEBUG=&lt;True|False&gt;  
ALLOWED_HOSTS=&lt;allowed hosts&gt;  
DB_HOST=db  
DB_NAME=&lt;database&gt;  
DB_USER=&lt;username&gt;  
DB_PASSWORD=&lt;password&gt;  
SECRET_KEY=&lt;secret key&gt;  
GOOGLE\_MAPS\_API_KEY=&lt;api key&gt;  

###Create pg.env

> POSTGRES_DB=&lt;database&gt;  
POSTGRES_USER=&lt;username&gt;  
POSTGRES_PASSWORD=&lt;password&gt;  

###Setup
1. run git clone https://github.com/acaciawater/rapid.git
2. dump existing database using pg_dump and put the sql file in the ./intdb.d directory (optional)
3. add ./media folder with maps and documents (optional)
4. run docker-compose up
