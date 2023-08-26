import streamlit as st

def main():
    st.title("Simple Streamlit App")
    user_input = st.text_input("Enter your text:")
    
    # Displaying user input
    st.write("You entered:", user_input)

if __name__ == "__main__":
    main()
