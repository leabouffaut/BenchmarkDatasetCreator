import streamlit as st


def add_numbers(num1, num2):
    return num1 + num2


def square_number(number):
    return number ** 2


def main():
    st.title("Simple Arithmetic Operations App")

    # User input fields
    num1 = st.number_input("Enter first number:")
    num2 = st.number_input("Enter second number:")

    # Initialize result if not already in session state
    if 'result' not in st.session_state:
        st.session_state.result = None

    result_message = None  # Define result_message here

    # Button to trigger addition
    if st.button("Add"):
        # Perform addition
        st.session_state.result = add_numbers(num1, num2)

        # Display result
        result_message = st.success(f"The sum of {num1} and {num2} is: {st.session_state.result}")

    # Button to trigger square operation
    if st.session_state.result is not None:
        if st.button("Square"):
            # Perform square operation on the result
            squared_result = square_number(st.session_state.result)

            # Display squared result
            st.success(f"The square of the sum is: {squared_result}")

            # Update message from "Add" button if it exists
            if result_message:
                result_message.text(f"The sum of {num1} and {num2} is: {st.session_state.result}")


if __name__ == "__main__":
    main()
