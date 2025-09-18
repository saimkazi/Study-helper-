from customtkinter import *
import customtkinter as ctk
import mysql.connector
import pymysql



db_connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="nea"
    )
cursor = db_connection.cursor()



                   
