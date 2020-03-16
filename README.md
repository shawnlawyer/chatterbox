# NLP Classifier with Tensorflow and Pandas on Flask and Jupyter Notebook

## Build and Run the Application 

- cp .env .env.example
  
- docker-compose up -d --build  

>Shell into main container
> docker exec -it chatterbox_app_1 bash  
 
- Restore the example chatterbox.dump file to a MySQL database `data` , username `data`, password `data`
  
- Browse to http://localhost/

- Type `hello` in the message field, and hit enter/return key

- Type `Log me in` in the message field, and hit enter/return key

- Type `admin@email.com` in the message field, and hit enter/return key

- Type `password` in the message field, and hit enter/return key

- In a new tab, browse to http://localhost/admin

- To logout, type `logout` in the message field, and hit enter/return key

- Alternately you can go the out fashioned route:
 
  >Login Form: http://localhost/admin/login
  
  >Logout: http://localhost/admin/logout
  
## Access the Jupyter Notebook 
  
- Shell into jupyter container
docker exec -it chatterbox_jupyter_1 bash  
  
- Run 
jupyter notebook list
**or**
hit the up arrow to revisit bash history and find 'jupyter notebook list' and hit enter.  
  > example output: http://0.0.0.0:8888/?token=fd54a13bceabddbda89ce0e66e31989a1b54f8eb9e650339 :: /notebooks  
  
- Browse to http://localhost:8888/?token=<token_value>  

