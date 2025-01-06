;; Problem definition
(define (problem problem-1)

  ;; Specifying the domain for the problem
  (:domain travel-domain)

  ;; Objects definition
  (:objects
    ; airports
    AP1
    AP2
    AP3
    ; stations
    S11
    S12
    S21
    S22
    S31
    ; Persons
    person1
    person2
    ; Vehicles
    plane1
    plane2
    train1
    train2
    train3
  )

  ;; Intial state of problem 1
  (:init
    ;; Declaration of the objects
    ; We initialize the airports
    (AIRPORT AP1)
    (AIRPORT AP2)
    (AIRPORT AP3)
    ; stations
    (STATION S11)
    (STATION S12)
    (STATION S21)
    (STATION S22)
    (STATION S31)
    ; Persons
    (PERSON person1)
    (PERSON person2)
    ; Vehicles
    (VEHICLE plane1)
    (VEHICLE plane2)
    (VEHICLE train1)
    (VEHICLE train2)
    (VEHICLE train3)

    (AIRPLANE plane1)
    (AIRPLANE plane2)
    (SUBWAY train1)
    (SUBWAY train2)
    (SUBWAY train3)
    ; Links
    (connected AP1 AP2) (connected AP2 AP1)
    (connected S11 S12) (connected S12 S11) 
    (connected AP1 S11) (connected S11 AP1)
    (connected AP1 S12) (connected S12 AP1)
    (connected S21 S22) (connected S22 S21) 
    (connected AP2 S21) (connected S21 AP2)
    (connected AP2 S22) (connected S22 AP2)
    (connected AP1 AP3) (connected AP3 AP1)
    (connected AP2 AP3) (connected AP3 AP2)
    (connected AP3 S31) (connected S31 AP3)
    
    ;; Declaration of the predicates of the objects
    ; We set vehicles locations
    (is-vehicle-at plane1 AP1)
    (is-vehicle-at plane2 AP2)
    (is-vehicle-at train1 AP1)
    (is-vehicle-at train2 AP2)
    (is-vehicle-at train3 AP3)
    ; We set the person initial position
    (is-person-at person1 S11)
    (is-person-at person2 S31)
  )

  ;; Goal specification
  (:goal
    (and
      ; We want person at S22
      (is-person-at person1 S21)
      (is-person-at person2 S12)
    )
  )

)
