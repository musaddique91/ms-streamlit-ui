import streamlit as st
import os
import tempfile
from chat.model_util import get_qa_chain
from chat.document_processor import process_documents

def process_chat():
    # Initialize session state variables if they don't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()

    # Application title
    st.title("📚 Document Q&A Assistant")

    # Create a two-column layout for the top section
    col1, col2 = st.columns([2, 1])

    with col1:
        # Upload section in the main area
        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF, DOCX, or TXT files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )

        # Display uploaded files
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} files")

            # Process new files
            new_files = [f for f in uploaded_files if f.name not in st.session_state.processed_files]
            if new_files:
                with st.spinner("Processing documents..."):
                    # Save files temporarily
                    temp_dir = tempfile.mkdtemp()
                    temp_paths = []
                    for file in new_files:
                        # Create a temporary file path
                        temp_path = os.path.join(temp_dir, file.name)
                        # Write the file to the temporary path
                        with open(temp_path, "wb") as f:
                            f.write(file.getvalue())
                        temp_paths.append(temp_path)

                    # Process documents
                    try:
                        vectorstore = process_documents(temp_paths)

                        # If we already have a vectorstore, merge the results
                        if st.session_state.vectorstore:
                            st.session_state.vectorstore.merge_from(vectorstore)
                        else:
                            st.session_state.vectorstore = vectorstore

                        # Update processed files list
                        st.session_state.processed_files.update([f.name for f in new_files])

                        # Create QA chain
                        st.session_state.qa_chain = get_qa_chain(st.session_state.vectorstore)

                        st.success("Documents processed successfully!")
                    except Exception as e:
                        st.error(f"Error processing documents: {str(e)}")

                    # Clean up temporary files
                    for temp_path in temp_paths:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)

    with col2:
        # Instructions in the second column
        st.markdown("""
        ### Instructions
        1. Upload your documents (PDF, DOCX, TXT)
        2. Wait for processing to complete
        3. Ask questions in the chat
        4. Get answers based on your documents
        """)

        # List processed files
        if st.session_state.processed_files:
            st.subheader("Processed Files:")
            for file_name in st.session_state.processed_files:
                st.write(f"✅ {file_name}")

    # Add a separator
    st.markdown("---")

    # Main area for chat interaction
    if st.session_state.vectorstore is not None:
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])

        # Chat input
        user_question = st.chat_input("Ask a question about your documents")

        if user_question:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_question})

            # Display user message
            with st.chat_message("user"):
                st.write(user_question)

            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Get response from QA chain
                    response = st.session_state.qa_chain(
                        {"question": user_question,
                         "chat_history": [(msg["content"], st.session_state.chat_history[i + 1]["content"])
                                          for i, msg in enumerate(st.session_state.chat_history[:-1:2])]}
                    )
                    answer = response["answer"]

                    # Display response
                    st.write(answer)

                    # Add assistant message to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    else:
        # Instructions when no documents are uploaded
        st.info("⬆️ Please upload documents above to get started.")
        st.write("You can upload PDF, DOCX, or TXT files to ask questions about their content.")
