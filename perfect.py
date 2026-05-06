import math

def is_prime(n):
    """Checks if a given integer n is a prime number."""
    if n <= 1:
        return False
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
    if n <= 1:
        return False
    
    sum_of_divisors = 1  # Start with 1, as it is always a proper divisor
    
    # Iterate up to the square root of n for efficiency
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            sum_of_divisors += i
            # Add the corresponding pair divisor (n/i), unless it's the square root itself
            if i * i != n:
                sum_of_divisors += (n // i)
    
    return sum_of_divisors == n

def find_primes_up_to(limit):
    """Generates a list of all prime numbers up to the specified limit."""
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
    print("\n" + "="*50)
    print("Testing Euclid-Euler Theorem (Even Perfect Numbers)")
    print("="*50)
    
    # We only need to test prime values for p
    prime_exponents = [p for p in range(2, max_p + 1) if is_prime(p)]
    
    for p in prime_exponents:
        # 1. Check if the Mersenne candidate (2^p - 1) is prime
        mersenne_candidate = (2**p) - 1
        
        if is_prime(mersenne_candidate):
            # 2. If it is prime, calculate the corresponding perfect number: N = 2^(p-1) * (2^p - 1)
            perfect_number = (2**(p - 1)) * mersenne_candidate
            print(f"✅ p={p}: Mersenne Prime found ({mersenne_candidate}).")
            print(f"   -> Generated Perfect Number: {perfect_number}")
        else:
            print(f"❌ p={p}: Mersenne candidate ({mersenne_candidate}) is NOT prime.")


# ==================================================
# --- MAIN EXECUTION BLOCK ---
# ==================================================

# 1. Test for Perfect Numbers up to a certain limit (e.g., 10,000)
LIMIT_PERFECT = 10000000
print(f"--- Searching for Perfect Numbers up to {LIMIT_PERFECT} ---")
perfects = []
for i in range(1, LIMIT_PERFECT + 1):
    if is_perfect(i):
        perfects.append(i)

if perfects:
    print("✅ Perfect Numbers Found:")
    print(", ".join(map(str, perfects)))
else:
    print("No perfect numbers found in this range.")

# 2. Locate Prime Numbers up to a certain limit (e.g., 10,000)
LIMIT_PRIME = 10000000
print(f"\n--- Locating Prime Numbers up to {LIMIT_PRIME} ---")
all_primes = find_primes_up_to(LIMIT_PRIME)
print(f"Total primes found: {len(all_primes)}")
# Displaying the first 20 for brevity
print("First 40 primes:", all_primes[:40])


# 3. Demonstrate the Euclid-Euler Theorem (Testing up to p=17)
test_euclid_euler(max_p=21)


