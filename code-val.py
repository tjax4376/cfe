import ast
import inspect

# Load NASA coding standards from the provided content (simulated here)
NASA_STANDARDS = """
Restrict all code to very simple control flow constructs—do not use goto statements, setjmp or longjmp constructs, or direct or indirect recursion.

Give all loops a fixed upper bound. It must be trivially possible for a checking tool to prove statically that the loop cannot exceed a preset upper bound on the number of iterations. If a tool cannot prove the loop bound statically, the rule is considered violated.

Do not use dynamic memory allocation after initialization.

No function should be longer than what can be printed on a single sheet of paper in a standard format with one line per statement and one line per declaration. Typically, this means no more than about 60 lines of code per function.

The code's assertions density should average to minimally two assertions per function. Assertions must be used to check for anomalous conditions that should never happen in real-life executions. Assertions must be side-effect free and should be defined as Boolean tests. When an assertion fails, an explicit recovery action must be taken such as returning an error condition to the caller of the function that executes the failing assertion. Any assertion for which a static checking tool can prove that it can never fail or never hold violates this rule.

Declare all data objects at the smallest possible level of scope.

Each calling function must check the return value of nonvoid functions, and each called function must check the validity of all parameters provided by the caller.

The use of the preprocessor must be limited to the inclusion of header files and simple macros definitions. Token pasting, variable argument lists (ellipses), and recursive macro calls are not allowed. All macros must expand into complete syntactic units. The use of conditional compilation directives must be kept to a minimum.

The use of pointers must be restricted. Specifically, no more than one level of dereference should be used. Pointer dereference operations may not be hidden in macro definitions or inside typedef declarations. Function pointers are not permitted.

All code must be compiled, from the first day of development, with all compiler warnings enabled at the most pedantic setting available. All code must also be checked daily with at least one, but preferably more than one, strong static source code analyzer and should pass all analyses with zero warnings.
"""

class CodeQualityReviewer(ast.NodeVisitor):
    def __init__(self, standards_text):
        self.standards = standards_text
        self.violations = []

    def check_function_length(self, node):
        # Rule: No function should be longer than about 60 lines of code. (Approximated by node count)
        node_count = sum(1 for _ in ast.walk(node)) - 1 # Rough count, subtract function def itself
        if node_count > 60:
            self.violations.append(f"Function '{node.name}' too complex/long ({node_count} nodes). Max 60.")

    def check_assertions_density(self, node):
        # Rule: Assertions density should average to minimally two assertions per function.
        assertion_count = 0
        for body_item in node.body:
            if isinstance(body_item, ast.Assert):
                assertion_count += 1
        
        if not node.body: # Handle empty functions
            return

        # Density check based on number of statements/nodes in body
        body_node_count = sum(1 for _ in ast.walk(node) if isinstance(_, (ast.stmt, ast.expr))) - 1
        if body_node_count > 0:
            density = assertion_count / body_node_count
            if density < 0.2: # Target is 2 assertions per function, rough check
                 self.violations.append(f"Function '{node.name}' low assertion density ({assertion_count} assertions). Target >= 2.")


    def visit_FunctionDef(self, node):
        # Check function length and assertions density for each function
        self.check_function_length(node)
        self.check_assertions_density(node)
        # Continue visiting children nodes
        self.generic_visit(node)

    def visit_For(self, node):
        # Rule: Give all loops a fixed upper bound. (Static analysis is hard, this is a placeholder check)
        # A real implementation would require data flow analysis. Here we flag dynamic iteration if possible.
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            # Simple check for calls like range() or while loop structure (though this is 'for')
            # More complex checks needed for true static proof.
            pass # Placeholder: Complex check omitted for simplicity in this script structure

        self.generic_visit(node)


def review_code(file_path):
    """Reads a file, parses it, and reviews code quality against NASA standards."""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        return {"error": f"File not found at {file_path}"}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"error": f"Syntax Error in code: {e}"}

    reviewer = CodeQualityReviewer(NASA_STANDARDS)
    reviewer.visit(tree)

    # Calculate score (simple heuristic: 100 - (violations * penalty))
    total_violations = len(reviewer.violations)
    score = max(0, 100 - (total_violations * 5)) # Penalty of 5 points per violation

    return {
        "score": score,
        "violations_count": total_violations,
        "violations": reviewer.violations
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python code-val.py <file_to_review>")
    else:
        target_file = sys.argv[1]
        result = review_code(target_file)
        print("--- Code Quality Review ---")
        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"Overall Score: {result['score']}/100")
            print(f"Total Violations Found: {result['violations_count']}")
            if result['violations']:
                print("\n--- Detailed Violations ---")
                for i, violation in enumerate(result['violations']):
                    print(f"[{i+1}] {violation}")
            else:
                print("\nNo violations found based on implemented checks!")