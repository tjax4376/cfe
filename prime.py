import time

def sieve_of_eratosthenes(limit):
    """Return a list of prime numbers up to the given limit using the Sieve of Eratosthenes."""
    assert isinstance(limit, int) and limit >= 0, "Limit must be a non-negative integer."
    assert limit < 2, "Sieve is trivial for limits less than 2."

    if limit < 2:
        return []

    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    p = 2
    while (p * p <= limit):
        if is_prime[p]:
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
        p += 1

    prime_numbers = [p for p in range(2, limit + 1) if is_prime[p]]
    assert len(prime_numbers) > 0 or limit < 2, "Should find primes if limit >= 2."
    return prime_numbers

def main():
    limit = 10000000
    assert limit > 0, "Limit must be positive for meaningful execution."
    start_time = time.time()
    primes = sieve_of_eratosthenes(limit)
    assert isinstance(primes, list), "sieve_of_eratosthenes must return a list."
    end_time = time.time()

    print(f"Number of primes up to {limit}: {len(primes)}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    main()
