# Poll Project

If you are interested in open source, you are always welcome to make some contributions!

* Version: 1.0
* Date Updated: 06/01/21 (DD/MM/YY order)

Contents:

1. [Overview](#1-Overview)
2. [How To Use Program](#2-How-To-Use-Program)
3. [Technical Details](#3-Technical-Details)
4. [Also](#4-Also)

## 1. Overview
This is my pet project. I have done it to expand my experience in [Django Web Framework](https://www.djangoproject.com). Poll Project helps communities make elections
to choose a candidate for some position. In the current situation, it is done to choose a president but it can be simply changed.
Everyone can make a choice and become a candidate. To control if the form is correct there is a moderator system. Also there is an 
admin system to control the whole process.

## 2. How To Use Program
When you first open the web page, you have to pass the registration process.

### Elector experience
After that you have an Elector status. You can read more about a specific candidate, choose a candidate you like and take part in elections. 
Important to notice, you have only one opportunity to vote, and after you have become a candidate, you can’t switch back to Elector status.

### Candidate experience
If you are a candidate, you still have an opportunity to vote. After you have finished writing the participation form, you have to send it 
and wait until it will be checked by the moderator. If your form is accepted, you will gain a notification about it. Otherwise, you will also 
take a notice with a reason for refusal.

### Moderator experience
To become moderator, you have to have a deal with your administrator. In the moderator page you can read an instruction for the job and moderate 
other users. You can’t visit pages which are acceptable for Elector and Candidate, and they too can’t see pages available for you.

### Admin experience
You can visit all pages available for Elector, Moderator and Candidate. However, IT IS STRONGLY RECOMMENDED to not do anything. If you want to
control the web page, you need to write `admin` after the domain `my-site.com/admin`. But you can change an instruction on the moderator's pag
if you click the `Instruction` button.


## 3. Technical Details
In the project there are the groups and roles system to restrict access to pages.

There are three types of roles:

  1. Elector
  2. Candidate
  3. Moderator
 
And five types of groups:

  1. Voted
  2. Application Process
  3. Application Draft
  4. Application Final 
  5. Admin (the standard superuser provided with Django Framework) 
 
Groups can be divided into three subgroups: for everyone - 1 group, for a Candidate - 2, 3, 4 gr. and system group - 5 gr. 
First group shows if a user is voted. Second, third and fourth show status of candidate application: if he only begin creating 
the candidate form, he will have Application Process status; if he save the form but hasn’t finished yet or if his forms 
hasn’t been accessed by Moderator, he will has Application Draft one; if everything is alright and he has gained permission from 
Moderator, he will be Application Final one.

To undestand the concept better, please watch this scheme: https://i.imgur.com/Pq4tF8J.jpg.

## 4. Also
1. If you are an administrator, it is strongly recommended using only Moderator’s pages and admin panel to not raise some 
bugs (the code is still under work).
2. Every view is divided on the classes: standard, participate, moderator and notification to simplify future development.  

### Contacts 
* e-mail: [morozovantonaleksandrovich@gmail.com](mailto:morozovantonaleksandrovich@gmail.com)
* telegram: [anomorch](https://t.me/anomorch) (preferable) 
