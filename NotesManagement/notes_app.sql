create database notes_app;
use notes_app;
create table users (id int primary key auto_increment,
					username varchar(100) not null,
                    email varchar(150) not null unique,
                    password varchar(255) not null,
                    created_at timestamp default current_timestamp);
create table notes (id int primary key auto_increment,
					user_id int not null,
                    content text not null,
                    created_at timestamp default current_timestamp,
                    constraint fk_notes_user foreign key(user_id) references users(id)
                    on delete cascade
                    on update cascade);
                    
