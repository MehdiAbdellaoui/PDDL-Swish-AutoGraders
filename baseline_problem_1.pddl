;; Problem definition
(define (problem problem-1)

  ;; Specifying the domain for the problem
  (:domain travel-domain)

  ;; Objects definition
  (:objects
    ; airports
    AP1
    AP2
    ; stations
    S11
    S12
    S21
    S22
    ; Persons
    person
    ; Vehicles
    plane
    train1
    train2
  )

  ;; Intial state of problem 1
  (:init
    ;; Declaration of the objects
    ; We initialize the airports
    (AIRPORT AP1)
    (AIRPORT AP2)
    ; stations
    (STATION S11)
    (STATION S12)
    (STATION S21)
    (STATION S22)
    ; Persons
    (PERSON person)
    ; Vehicles
    (VEHICLE plane)
    (VEHICLE train1)
    (VEHICLE train2)
    (AIRPLANE plane)
    (SUBWAY train1)
    (SUBWAY train2)
    ; Links
    (connected AP1 AP2) (connected AP2 AP1)
    (connected S11 S12) (connected S12 S11) 
    (connected AP1 S11) (connected S11 AP1)
    (connected AP1 S12) (connected S12 AP1)
    (connected S21 S22) (connected S22 S21) 
    (connected AP2 S21) (connected S21 AP2)
    (connected AP2 S22) (connected S22 AP2)
    
    ;; Declaration of the predicates of the objects
    ; We set vehicles locations
    (is-vehicle-at plane AP2)
    (is-vehicle-at train1 AP1)
    (is-vehicle-at train2 AP2)
    ; We set the person initial position
    (is-person-at person S11)
  )

  ;; Goal specification
  (:goal
    (and
      ; We want person at S22
      (is-person-at person S22)
    )
  )

)
