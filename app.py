"""
FileRAG - File-based Retrieval Augmented Generation using Google Gemini
Main Streamlit Application
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src import GeminiClient, StoreManager, DocumentManager, ChatHandler

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FileRAG - Document Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-success {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .status-error {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .status-info {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'gemini_client' not in st.session_state:
        st.session_state.gemini_client = None
    if 'store_manager' not in st.session_state:
        st.session_state.store_manager = None
    if 'document_manager' not in st.session_state:
        st.session_state.document_manager = None
    if 'chat_handler' not in st.session_state:
        st.session_state.chat_handler = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_key_validated' not in st.session_state:
        st.session_state.api_key_validated = False


def setup_sidebar():
    """Configure sidebar with API key and navigation"""
    with st.sidebar:
        st.markdown("### 🔑 Configuration")

        # API Key input
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Enter your Google Gemini API key. Get one at https://aistudio.google.com/"
        )

        if api_key:
            if not st.session_state.api_key_validated:
                try:
                    # Initialize Gemini client
                    st.session_state.gemini_client = GeminiClient(api_key)
                    st.session_state.store_manager = StoreManager(st.session_state.gemini_client)
                    st.session_state.api_key_validated = True
                    st.success("API Key validated!")
                except Exception as e:
                    st.error(f"Invalid API Key: {str(e)}")
                    return False

            # Show store status
            if st.session_state.store_manager:
                st.markdown("---")
                st.markdown("### 📊 Store Status")

                store_info = st.session_state.store_manager.get_store_info()

                if store_info['exists']:
                    st.success("✅ Store Active")
                    st.write(f"**Documents:** {store_info.get('document_count', 0)}")
                    st.write(f"**Created:** {store_info.get('created_at', 'Unknown')[:10]}")
                else:
                    st.warning("⚠️ No Store Configured")

                st.markdown("---")

            return True
        else:
            st.info("👆 Please enter your Gemini API key to get started")
            st.markdown("---")
            st.markdown("### 📖 How to get API Key")
            st.markdown("""
            1. Visit [Google AI Studio](https://aistudio.google.com/)
            2. Sign in with your Google account
            3. Click "Get API key"
            4. Create or select a project
            5. Copy your API key
            """)
            return False


def render_store_management():
    """Render Store Management tab"""
    st.markdown("## 🗄️ Store Management")
    st.write("Create and manage your document store (corpus)")

    store_info = st.session_state.store_manager.get_store_info()

    if store_info['exists']:
        # Display store information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Status", "Active", "✅")
        with col2:
            st.metric("Documents", store_info.get('document_count', 0))
        with col3:
            created_date = store_info.get('created_at', 'Unknown')
            if created_date != 'Unknown':
                created_date = created_date[:10]
            st.metric("Created", created_date)

        st.markdown("---")

        # Store details
        with st.expander("📋 Store Details", expanded=False):
            st.write(f"**Store Name:** {store_info.get('store_name', 'Unknown')}")

        # Delete store option
        st.markdown("### ⚠️ Danger Zone")
        if st.button("🗑️ Delete Store", type="secondary"):
            if st.session_state.get('confirm_delete', False):
                result = st.session_state.store_manager.delete_store()
                if result['success']:
                    st.success(result['message'])
                    st.session_state.document_manager = None
                    st.session_state.chat_handler = None
                    st.session_state.chat_history = []
                    st.session_state.confirm_delete = False
                    st.rerun()
                else:
                    st.error(result['message'])
            else:
                st.session_state.confirm_delete = True
                st.warning("⚠️ Click 'Delete Store' again to confirm deletion. This action cannot be undone!")

    else:
        # Create new store
        st.info("📝 No store configured. Create a new store to get started.")

        store_name = st.text_input(
            "Store Name",
            value="filerag_store",
            help="Enter a name for your document store"
        )

        if st.button("🚀 Create Store", type="primary"):
            with st.spinner("Creating store..."):
                result = st.session_state.store_manager.create_store(store_name)

                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")


def render_document_management():
    """Render Document Management tab"""
    st.markdown("## 📄 Document Management")
    st.write("Upload, view, and delete documents in your store")

    # Check if store exists
    if not st.session_state.store_manager.store_exists():
        st.warning("⚠️ Please create a store first in the 'Store Management' tab")
        return

    # Initialize document manager if needed
    if not st.session_state.document_manager:
        store_name = st.session_state.store_manager.get_store_name()
        st.session_state.document_manager = DocumentManager(
            st.session_state.gemini_client,
            store_name
        )

    # Create two columns for layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📤 Upload Documents")

        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=['txt', 'pdf', 'doc', 'docx', 'md'],
            help="Upload documents to add to your store"
        )

        if uploaded_files:
            st.write(f"**{len(uploaded_files)} file(s) selected**")

            if st.button("Upload All", type="primary"):
                with st.spinner("Uploading documents..."):
                    results = st.session_state.document_manager.batch_upload_documents(uploaded_files)

                    # Show results
                    st.success(f"✅ Successfully uploaded {results['successful']} document(s)")
                    if results['failed'] > 0:
                        st.warning(f"⚠️ Failed to upload {results['failed']} document(s)")

                    # Show details
                    with st.expander("📋 Upload Details"):
                        for detail in results['details']:
                            if detail['success']:
                                st.success(f"✅ {detail['file']}")
                            else:
                                # Check if it's a duplicate (warning) or actual error
                                if 'already exists' in detail['message']:
                                    st.warning(f"⚠️ {detail['file']}: {detail['message']}")
                                else:
                                    st.error(f"❌ {detail['file']}: {detail['message']}")

                    st.rerun()

    with col2:
        st.markdown("### 🗑️ Delete Documents")

        try:
            documents = st.session_state.document_manager.list_documents()

            if documents:
                # Create a selection dropdown
                doc_options = {doc['display_name']: doc['name'] for doc in documents}
                selected_doc_display = st.selectbox(
                    "Select document to delete",
                    options=list(doc_options.keys())
                )

                if st.button("Delete Selected", type="secondary"):
                    selected_doc_name = doc_options[selected_doc_display]

                    with st.spinner("Deleting document..."):
                        result = st.session_state.document_manager.delete_document(selected_doc_name)

                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
            else:
                st.info("No documents in store")

        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")

    # List all documents
    st.markdown("---")
    st.markdown("### 📚 All Documents")

    try:
        documents = st.session_state.document_manager.list_documents()

        if documents:
            # Create a table view
            import pandas as pd

            df = pd.DataFrame([
                {
                    'Name': doc['display_name'],
                    'Created': doc['create_time'][:19] if doc['create_time'] != 'Unknown' else 'Unknown',
                    'Updated': doc['update_time'][:19] if doc['update_time'] != 'Unknown' else 'Unknown'
                }
                for doc in documents
            ])

            st.dataframe(df, use_container_width=True)
            st.caption(f"Total documents: {len(documents)}")

            # Add detailed verification section
            with st.expander("🔍 Verify Document Status (Debug Info)", expanded=False):
                st.write("**Checking file status in Gemini...**")

                import google.generativeai as genai

                for doc in documents:
                    try:
                        file = genai.get_file(doc['name'])
                        status = file.state.name if hasattr(file, 'state') else 'UNKNOWN'

                        if status == 'ACTIVE':
                            st.success(f"✅ {doc['display_name']}: **{status}** (Ready for queries)")
                        elif status == 'PROCESSING':
                            st.warning(f"⏳ {doc['display_name']}: **{status}** (Still processing, wait a moment)")
                        elif status == 'FAILED':
                            st.error(f"❌ {doc['display_name']}: **{status}** (Upload failed)")
                        else:
                            st.info(f"ℹ️ {doc['display_name']}: **{status}**")

                    except Exception as e:
                        st.error(f"❌ {doc['display_name']}: Error - {str(e)}")

        else:
            st.info("📭 No documents in store. Upload documents to get started!")

    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")


def render_chat_interface():
    """Render Chat/Query Interface tab"""
    st.markdown("## 💬 Ask Questions")
    st.write("Query your documents and get intelligent answers")

    # Check if store exists
    if not st.session_state.store_manager.store_exists():
        st.warning("⚠️ Please create a store and upload documents first")
        return

    # Check if there are documents
    if not st.session_state.document_manager:
        store_name = st.session_state.store_manager.get_store_name()
        st.session_state.document_manager = DocumentManager(
            st.session_state.gemini_client,
            store_name
        )

    doc_count = st.session_state.document_manager.get_document_count()

    if doc_count == 0:
        st.warning("⚠️ No documents in store. Upload documents in the 'Document Management' tab")
        return

    # Initialize chat handler if needed
    if not st.session_state.chat_handler:
        st.session_state.chat_handler = ChatHandler(
            st.session_state.gemini_client,
            st.session_state.document_manager
        )

    # Display chat history
    for idx, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                # Display sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("📎 Sources"):
                        for source in message["sources"]:
                            st.write(f"**{source['index']}.** {source['document']}")
                            if source.get('chunk'):
                                st.caption(source['chunk'][:200] + "...")

                # Display rating if already rated
                if message.get('rating') or message.get('note'):
                    st.markdown("---")
                    st.caption(f"⭐ **Rating:** {message.get('rating', 'Not rated')} / 5")
                    if message.get('note'):
                        st.caption(f"📝 **Note:** {message['note']}")

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                response = st.session_state.chat_handler.query(prompt)
                formatted = st.session_state.chat_handler.format_response_for_display(response)

                if formatted['has_answer']:
                    st.markdown(formatted['answer'])

                    # Display sources
                    if formatted['sources']:
                        with st.expander("📎 Sources"):
                            for source in formatted['sources']:
                                st.write(f"**{source['index']}.** {source['document']}")
                                if source.get('chunk'):
                                    st.caption(source['chunk'][:200] + "...")
                else:
                    st.warning(formatted['message'])

                # Show debug info if available
                if 'debug_info' in response and response['debug_info']:
                    with st.expander("🐛 Debug Info", expanded=False):
                        st.json(response['debug_info'])

                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": formatted['answer'] if formatted['has_answer'] else formatted['message'],
                    "sources": formatted['sources'],
                    "rating": None,
                    "note": None,
                    "question": prompt
                })

    # Rating form for the last assistant message (if not rated yet)
    if st.session_state.chat_history:
        last_message = st.session_state.chat_history[-1]
        if last_message["role"] == "assistant" and last_message.get("rating") is None:
            st.markdown("---")
            st.markdown("### ⭐ Rate this answer")

            rating = st.radio(
                "Quality",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: f"{'⭐' * x} ({x})",
                horizontal=False,
                key="rating_input"
            )

            note = st.text_input(
                "Add a note (optional)",
                placeholder="Enter any feedback or comments...",
                key="note_input"
            )

            if st.button("💾 Save Rating", type="primary"):
                # Update the last message with rating and note
                st.session_state.chat_history[-1]["rating"] = rating
                st.session_state.chat_history[-1]["note"] = note if note else None

                # Save rating to log file
                st.session_state.chat_handler.save_rating(
                    question=last_message["question"],
                    answer=last_message["content"],
                    rating=rating,
                    note=note
                )

                st.success("✅ Rating saved!")
                st.rerun()

    # Sidebar for chat controls
    with st.sidebar:
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 💬 Chat Controls")

            query_count = st.session_state.chat_handler.get_query_count()
            st.metric("Total Queries", query_count)

            if st.button("🔄 Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

            # Download query history
            history = st.session_state.chat_handler.get_query_history()
            st.download_button(
                label="📥 Download History",
                data=history,
                file_name=f"query_history_{st.session_state.store_manager.get_store_name()}.txt",
                mime="text/plain"
            )


def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">📚 FileRAG</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">File-based Retrieval Augmented Generation with Google Gemini</div>',
        unsafe_allow_html=True
    )

    # Setup sidebar
    if not setup_sidebar():
        st.info("👈 Please configure your API key in the sidebar to get started")
        return

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🗄️ Store Management", "📄 Document Management", "💬 Ask Questions"])

    with tab1:
        render_store_management()

    with tab2:
        render_document_management()

    with tab3:
        render_chat_interface()


if __name__ == "__main__":
    main()
