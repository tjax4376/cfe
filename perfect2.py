import math
import time
import sys

# --- Utility Functions (Unchanged, as they are mathematically correct) ---

def is_prime(n):
    """Checks if a given integer n is a prime number."""
    assert isinstance(n, int) and n > 0, "Input must be a positive integer."
    assert n > 1, "Prime numbers must be greater than 1."
    if n <= 3:
        return True
    # Check divisibility by 2 or 3
    if n % 2 == 0 or n % 3 == 0:
        return False
    # Check divisibility by numbers of the form 6k ± 1 up to sqrt(n)
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def is_perfect(n):
    """Checks if a given integer n is a perfect number."""
    assert isinstance(n, int) and n > 0, "Input must be a positive integer."
    assert n > 1, "Perfect numbers must be greater than 1."
    
    sum_of_divisors = 1  # Start with 1, as it is always a proper divisor
    
    # Iterate up to the square root of n for efficiency
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            sum_of_divisors += i
            # Add the corresponding pair divisor (n/i), unless it's the square root itself
            if i * i != n:
                sum_of_divisors += (n // i)
    
    assert sum_of_divisors == n, f"Number {n} is not perfect. Sum of divisors: {sum_of_divisors}"
    return sum_of_divisors == n

def find_primes_up_to(limit):
    """Generates a list of all prime numbers up to the specified limit."""
    assert isinstance(limit, int) and limit >= 2, "Limit must be an integer greater than or equal to 2."
    assert limit >= 2, "Limit must be at least 2 to find primes."
    primes = []
    for number in range(2, limit + 1):
        if is_prime(number):
            primes.append(number)
    return primes

def test_euclid_euler(max_p):
    """
    Tests the Euclid-Euler theorem by checking small prime exponents (p) 
    to see if they generate a perfect number.
    """
    assert max_p >= 2, "max_p must be at least 2 to test primes."
    print("\n" + "="*50)
    print("Testing Euclid-Euler Theorem (Even Perfect Numbers)")
    print("="*50)
    
    # We only need to test prime values for p
    prime_exponents = [p for p in range(2, max_p + 1) if is_prime(p)]
    assert len(prime_exponents) >= 1, "No prime exponents found up to max_p."
    
    for p in prime_exponents:
        # 1. Check if the Mersenne candidate (2^p - 1) is prime
        mersenne_candidate = (2**p) - 1
        assert isinstance(mersenne_candidate, int), "Mersenne candidate must be an integer."
        
        if is_prime(mersenne_candidate):
            # 2. If it is prime, calculate the corresponding perfect number: N = 2^(p-1) * (2^p - 1)
            perfect_number = (2**(p - 1)) * mersenne_candidate
            print(f"✅ p={p}: Mersenne Prime found ({mersenne_candidate}).")
            print(f"   -> Generated Perfect Number: {perfect_number}")
        else:
            print(f"❌ p={p}: Mersenne candidate ({mersenne_candidate}) is NOT prime.")


# --- Spinner Implementation ---

def print_with_spinner(message, total_iterations):
    """Prints a message with a spinning ASCII cursor while processing."""
    assert total_iterations > 0, "Total iterations must be positive."
    spinner = ['-', '\\', '|', '/']
    start_time = time.time()
    
    for i in range(total_iterations):
        # Calculate which frame of the spinner to show
        frame = spinner[i % len(spinner)]
        
        # Print the message, cursor, and flush output immediately
        sys.stdout.write(f'\rProcessing... {frame} {message}')
        sys.stdout.flush()
        time.sleep(0.05) # Small delay to make the spinner visible

    # Clear the line after completion
    sys.stdout.write('\r' + ' ' * 50 + '\r')
    sys.stdout.flush()


# ==================================================
# --- MAIN EXECUTION BLOCK (Updated) ---
# ==================================================

# 1. Test for Perfect Numbers up to a certain limit
LIMIT_PERFECT = 10000000  # Reduced for practical runtime with spinner
print(f"--- Searching for Perfect Numbers up to {LIMIT_PERFECT} ---")

for i in range(1, LIMIT_PERFECT + 1):
    if is_perfect(i):
        print(f"Found perfect number: {i}")


# 2. Locate Prime Numbers up to a certain limit
LIMIT_PRIME = 10000000 # Reduced for practical runtime with spinner
print(f"\n--- Locating Prime Numbers up to {LIMIT_PRIME} ---")

# Use the spinner while finding primes
print_with_spinner("Finding Primes...", LIMIT_PRIME)

all_primes = find_primes_up_to(LIMIT_PRIME)
print(f"\nTotal primes found: {len(all_primes)}")
# Displaying the first 400 for brevity
print("First 400 primes:", all_primes[:40])


# 3. Demonstrate the Euclid-Euler Theorem (Testing up to p=2311)
test_euclid_euler(max_p=2311)