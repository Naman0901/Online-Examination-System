DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS test;
DROP TABLE IF EXISTS que;
DROP TABLE IF EXISTS Faculty;
DROP TABLE IF EXISTS marks;

CREATE TABLE user(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email TEXT NOT NULL,
  u_type TEXT NOT NULL
);

CREATE TABLE student(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT UNIQUE NOT NULL,
 password TEXT NOT NULL,
 firstname TEXT NOT NULL,
 lastname TEXT NOT NULL,
 email TEXT NOT NULL,
 class text,
 rollno text,
 sem text,
 created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  tname TEXT NOT NULL,
  tsub TEXT NOT NULL,
  tmarks INTEGER NOT NULL,
  tstime TEXT not null,
  tduration TEXT not null,
  tsem INTEGER not null,
  tnoque INTEGER NOT null,
  tcreated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Faculty(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username text not null,
  password text not null,
  firstname text not null,
  lastname text not null,
  email text not null,
  subj text,
  dept text,
  CREATED TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE que(
  id integer PRIMARY KEY AUTOINCREMENT,
  testid integer not null,
  ques text not null,
  ans text not null,
  opt1 text NOT NULL,
  opt2 text not null,
  opt3 text not null,
  opt4 text not null, 
  queid int
);

CREATE TABLE marks(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  testid integer not null,
  uname text not null,
  userid INTEGER NOT NULL,
  mark INTEGER NOT NULL
);