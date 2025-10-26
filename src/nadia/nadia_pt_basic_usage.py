from nadia.nadia_pt_fo import check_proof

print(check_proof('''1. A|B              pre
2. A->C             pre
3. B->C             pre
4. {    A           hip
5.      C           ->e 4,2
   } 
6. {    B           hip
7.      C           ->e 6,3
   }
8. C                |e 1, 4-5, 6-7'''))

print(check_proof('''1. Ax (H(x) | M(x))        pre
2. Ex ~H(x)                pre
3. { a   ~H(a)             hip
4.         H(a) | M(a)     Ae 1
5.  {      H(a)            hip
6.           @             ~e 3,5
7.           Ex M(x)       @e 6
    }
8.  {      M(a)            hip
9.           Ex M(x)       Ei 8
    }
10.  Ex M(x)               |e 4,5-7,8-9
}
11. Ex M(x)                 Ee 2,3-10'''))

print(check_proof('''1. Ax (H(x)->M(x))         pre
2. Ex H(x)                 pre
3. { a   H(a)              hip
4.         H(a)->M(a)      Ae 1
5.         M(a)            ->e 3,4
6.         Ex M(x)         Ei 5
}
7. Ex M(x)                 Ee 2, 3-6'''))

print(check_proof('''1. A->(B->C)             pre
2. { B                    hip
3.  {  A                  hip
4.     B->C               ->e 3,1
5.     C                  ->e 2,4
    }
6. A->C                  ->i 3-5
}
7. B->(A->C)             ->i 2-6'''))



print(check_proof('''1. {    ~(A | ~A)            hip
2.  {   ~A                   hip
3.      A | ~A               |i 2
4.      @                    ~e 1,3
    }
5.  A                        raa 2-4
6.  A | ~A                   |i 5
7.  @                        ~e 1,6
}
8. A | ~A                    raa 1-7'''))

print(check_proof('''1. A&B->C                 pre
2. { B                    hip
3.  {  A                   hip
4.     A&B                 &i 3,2
5.     C                   ->e 1,4
   }
6. A->C                   ->i 3-5
}
7. B->(A->C)              ->i 2-6'''))


print(check_proof('''1. ~Ax ~P(x)                 pre
2. { ~Ex P(x)                hip
3.  { a
4.   { P(a)                  hip
5.     Ex P(x)               Ei 4
6.     @                     ~e 2,5
    }
7.   ~P(a)                   ~i 4-6
   }
8. Ax ~P(x)                   Ai 3-7
9. @                          ~e 1,8
}
10. Ex P(x)                   raa 2-9'''))

print(check_proof('''1. A|(A&B)          pre
2. {    A           hip
3.      A           copie 2
   }
4. {    A&B         hip
5.      A           &e 4
   }
6. (A|(A&B))->A     ->i 1-5'''))


print(check_proof('''1. Ax (H(x)|M(x))         pre
2. Ax ~M(x)               pre
3. { a
4.         H(a)|M(a)     Ae 1
5.  {      H(a)          hip
6.         H(a)          copie 5
    }
7.  {      M(a)          hip
8.         ~M(a)         Ae 2
9.         @             ~e 7,8
10.        H(a)          @e 9
    }
11. H(a)                  |e 4,5-6,7-10
}
12. Ax H(x)               Ai 3-11'''))