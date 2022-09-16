import streamlit as st

# call back function -> runs BEFORE the rest of the app
def reset_button():
    st.session_state["p"] = False
    return

#button to control reset
reset=st.button('Reset', on_click=reset_button)

#checkbox you want the button to un-check
check_box = st.checkbox("p", key='p')

#write out the current state to see that our flow works
st.write(st.session_state)