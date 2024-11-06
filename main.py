
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import src.agente as agente
import streamlit as st
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain.memory import ConversationBufferMemory

# Initialize the SQL agent
sql_agent = agente.agente_alive()

# Initialize the session state for memory if not already present
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(k=10,memory_key="chat_history", return_messages=True)
    


def convert_message_to_model_message(msg):
    """Convert a message dictionary to a model-specific message instance."""
    if msg["role"] == "user":
        return HumanMessage(content=msg["content"])
    elif msg["role"] == "assistant":
        return AIMessage(content=msg["content"])
    else:
        return None

def interface():
    st.title("💬 Huawei AI Chatbot")
    st.caption("🚀 IA Generativa para auxiliar nossos clientes")
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Como posso lhe ajudar?"}]

    # Display chat history
    for msg in st.session_state["messages"]:
        if msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        else:
            st.chat_message("user").write(msg["content"])

    # Handle new input
    if prompt := st.chat_input():
        # Create a new message for the user's input
        user_message = {"role": "user", "content": prompt}
        st.session_state["messages"].append(user_message)
        
        # Display the new user message immediately
        st.chat_message("user").write(user_message["content"])
        
        if sql_agent:
            try:
                # Ensure the historical messages are correctly formatted
                historical_messages = [
                    convert_message_to_model_message(msg) for msg in st.session_state["messages"]
                ]
                
                # Invoke the agent with the full conversation history
                result = sql_agent.invoke(
                    {"messages": historical_messages},
                    {"recursion_limit": 100}
                )
                
                assistant_response = result["messages"][-1].content if result["messages"] else "I couldn't process your request."
                assistant_message = {"role": "assistant", "content": assistant_response}
                
                # Append the response to the message history
                st.session_state["messages"].append(assistant_message)

                # Save the conversation context into the memory
                st.session_state["memory"].save_context({"input": prompt}, {"output": assistant_response})
                
                # Display the result
                st.chat_message("assistant").write(assistant_response)
            except Exception as e:
                st.chat_message("assistant").write(f"Error: {str(e)}")
        else:
            st.chat_message("assistant").write("Agent is not initialized!")

if __name__ == "__main__":
    interface()