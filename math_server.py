from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Arithmetic Calculator")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of a and b
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract second number from first number.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Difference (a - b)
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Product of a and b
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide first number by second number.
    
    Args:
        a: Numerator
        b: Denominator
    
    Returns:
        Quotient (a / b)
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise a number to a power.
    
    Args:
        base: Base number
        exponent: Exponent
    
    Returns:
        base raised to the power of exponent
    """
    return base ** exponent


@mcp.tool()
def modulo(a: float, b: float) -> float:
    """Calculate remainder of division.
    
    Args:
        a: Dividend
        b: Divisor
    
    Returns:
        Remainder of a divided by b
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot calculate modulo with zero divisor")
    return a % b
