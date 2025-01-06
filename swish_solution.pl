%%  friends(-Solution)
%   @param  Solution is a list of friends that satisfy all constraints.

/* 4 friends logical puzzle: 
* 
* The constants:
* Friends: p1, p2, p3, p4
* Season: summer, fall, winter, spring
* Hobbies: football, Dota2, tennis, LoL
* Housing: house, apartment
* Occupation: employee, student, unemployed
* 
* We define that:
*  Two people are neighbours if they live in the same type of housing.
* 
* And we know the following facts:
*  F1- p1 lives in a house;
*  F2- p4 plays tennis;
*  F3- p3 plays football;
*  F4- The person that plays football is an employee;
*  F5- The person who likes spring season is currently unemployed;
*  F6- The summer lover plays football, the fall lover plays Dota2, the winter lover plays tennis, and the spring lover plays LoL;
*  F7- The person who plays Dota2 lives in a house and is currently an employee;
*  F8- The person who loves winter does not live in a house and is a student;
*  F9- p2 and p4 are neighbors;
*  F10- The person who loves summer is a neighbour of p2, but not of p1;
*  F11- A neighbour of p3 plays tennis;
*/

% Render the houses term as a nice table.
:- use_rendering(table,[header(p('Person', 'Season', 'Hobbies', 'Housing', 'Occupation'))]).


%Two people are neighbours if they live in the same type of housing.
neighbours(P1, P2, Ls) :-				
    member(p(P1, _, _, X, _),Ls),
    member(p(P2, _, _, Y, _),Ls),
    not(P1 == P2),
    X = Y.

% The facts:
fact1(Ls) :- 
    member(p(p1,_,_,house,_), Ls).
fact2(Ls) :- 
    member(p(p4,_,tennis,_,_),Ls).	
fact3(Ls) :- 
    member(p(p3,_,football,_,_), Ls).
fact4(Ls) :-
    member(p(_, _, football, _, employee), Ls).
fact5(Ls) :-
    member(p(_,spring,_,_,unemployed),Ls).
fact6(Ls) :-
    member(p(_, summer, football, _, _),Ls),
    member(p(_, fall, dota2,_, _),Ls),		
    member(p(_, winter, tennis, _, _),Ls),
    member(p(_, spring, lol, _, _),Ls).
fact7(Ls) :-
    member(p(_, _, dota2, house, employee),Ls).
fact8(Ls) :-
    member(p(_, winter, _, X, Y),Ls),
    not(X == house),
    Y = student.
fact9(Ls) :- 
    neighbours(p2,p4,Ls). 
fact10(Ls) :-
    member(p(X, summer,_, _, _), Ls),
    neighbours(X, p2, Ls),
    not(neighbours(X, p1, Ls)).
fact11(Ls) :- 
    neighbours(X, p3, Ls),
    member(p(X, _,tennis,_,_),Ls).

% Problem:
friends(Ls) :-
    length(Ls, 4),						%There are 4 friends in our list Ls
    member(p(p1,_,_,_,_), Ls), member(p(p2,_,_,_,_), Ls), member(p(p3,_,_,_,_), Ls), member(p(p4,_,_,_,_), Ls), %One of them is p1, one is p2, one is p3, one is p4
    member(p(_,summer,_,_,_), Ls), member(p(_,fall,_,_,_), Ls), member(p(_,winter,_, _,_), Ls), member(p(_,spring,_, _,_), Ls), %One of them loves summer, one of them fall, one of them winter, one of them spring
    member(p(_,_,football,_,_), Ls), member(p(_,_,dota2, _,_), Ls), member(p(_,_,tennis, _,_), Ls), member(p(_,_,lol, _,_), Ls), %One of them plays football, one of them dota2, one of them tennis, and one of them lol
    member(p(_,_,_, house,_), Ls), member(p(_,_,_, apartment,_), Ls), %Some live in a house and some live in an apartment
    member(p(_,_,_, _,employee), Ls), member(p(_,_,_, _,student), Ls), member(p(_,_,_, _,unemployed), Ls), %Some are employees, some are students, some are unemployed
    fact1(Ls),
    fact2(Ls),
    fact3(Ls),
    fact4(Ls),
    fact5(Ls),
    fact6(Ls),
    fact7(Ls),
    fact8(Ls),
    fact9(Ls),
    fact10(Ls),
    fact11(Ls).
 

%To see the results, run ?- friends(Ls).