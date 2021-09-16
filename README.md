List of implemented methods:

+ Simulation (through the Ciw library)
+ Method 1 - Combine exact values from a Markov chain with the work of Masuyama and Takine (2003).
           - Code for Markov chain and the work of Masuyama and Takine (2003) is in `aux/models.py`.
           - Code for the combined methodology is in `jsq_ps/models.py`
+ Method 2 - Use the approximate method presented in (Gupta, Varun et al, 2007).
           - Code for the work of Gupta, Varun et al (2007) is in `aux.models.py`.
           - Wrapper code for the full method is in `jsq_ps/models.py`.


Repository structure:

- `jsq_ps/`: this contains the `models.py` file with all the classes required to calculate sojourn time cdfs for the JSQ-PR system.
- `aux/`: this contains any auxilliary classes and functions used in the intermediate stages. E.g the markov chain and single MM1-PR models.
- `tests/`: this contains any scripts or notebooks used to test or demonstrate the models defines in `aux/` and `jsq-ps/`.
- `experiments/`: this contains any numerical experiments for the paper.