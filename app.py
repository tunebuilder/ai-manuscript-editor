import streamlit as st
import os
from typing import Optional
from document_ingestion import extract_document_text
from chunking_engine import chunk_document_text, get_chunk_count, get_chunk_summary
from openai_editor import process_chunks_in_batches, get_editing_stats, load_system_prompt
from pdf_generator import create_pdf_bytes, get_pdf_filename, get_pdf_stats

# Configure page
st.set_page_config(
    page_title="AI Manuscript Editor",
    page_icon="📝",
    layout="wide"
)

def main():
    st.title("📝 AI Manuscript Editor")
    st.markdown("Transform your manuscript with AI-powered stylistic editing")
    
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'chunks' not in st.session_state:
        st.session_state.chunks = []
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'edited_chunks' not in st.session_state:
        st.session_state.edited_chunks = []
    if 'editing_complete' not in st.session_state:
        st.session_state.editing_complete = False
    if 'system_prompt' not in st.session_state:
        # Load default system prompt on first run
        st.session_state.system_prompt = load_system_prompt()
    if 'chunking_method' not in st.session_state:
        st.session_state.chunking_method = "daily"
    if 'paragraphs_per_chunk' not in st.session_state:
        st.session_state.paragraphs_per_chunk = 3
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            disabled=st.session_state.processing,
            help="Enter your OpenAI API key to enable AI editing"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key
        
        st.divider()
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=['pdf', 'docx'],
            disabled=st.session_state.processing,
            help="Upload a PDF or Word document containing journal entries"
        )
        
        st.divider()
        
        # Chunking Method Selection
        st.subheader("⚙️ Chunking Options")
        
        chunking_method = st.selectbox(
            "Chunking Method",
            options=["daily", "paragraph"],
            format_func=lambda x: "By daily journal entry" if x == "daily" else "By paragraph",
            index=0 if st.session_state.chunking_method == "daily" else 1,
            disabled=st.session_state.processing,
            help="Choose how to split your document into chunks for AI processing"
        )
        
        # Update session state if method changed
        if chunking_method != st.session_state.chunking_method:
            st.session_state.chunking_method = chunking_method
            # Reset chunks if method changed and we have existing chunks
            if st.session_state.chunks:
                st.session_state.chunks = []
                st.session_state.edited_chunks = []
                st.session_state.editing_complete = False
        
        # Paragraph count field (only show if paragraph method selected)
        if chunking_method == "paragraph":
            paragraphs_per_chunk = st.number_input(
                "Paragraphs per chunk",
                min_value=1,
                max_value=20,
                value=st.session_state.paragraphs_per_chunk,
                disabled=st.session_state.processing,
                help="Number of paragraphs to include in each chunk"
            )
            
            # Update session state if count changed
            if paragraphs_per_chunk != st.session_state.paragraphs_per_chunk:
                st.session_state.paragraphs_per_chunk = paragraphs_per_chunk
                # Reset chunks if count changed and we have existing chunks
                if st.session_state.chunks:
                    st.session_state.chunks = []
                    st.session_state.edited_chunks = []
                    st.session_state.editing_complete = False
        
        st.divider()
        
        # System Prompt Editor
        st.subheader("✏️ AI Editing Instructions")
        
        system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.system_prompt,
            height=200,
            disabled=st.session_state.processing,
            help="Customize the AI editing instructions. The default prompt focuses on stylistic enhancement while preserving structure.",
            placeholder="Enter your custom editing instructions here..."
        )
        
        # Update session state if prompt was modified
        if system_prompt != st.session_state.system_prompt:
            st.session_state.system_prompt = system_prompt
        
        # Show reset button to restore default
        if st.button("🔄 Reset to Default", disabled=st.session_state.processing, help="Restore the default editing instructions"):
            st.session_state.system_prompt = load_system_prompt()
            st.rerun()
        
        st.divider()
        
        # Begin Processing button
        begin_processing = st.button(
            "Begin Processing",
            type="primary",
            disabled=st.session_state.processing or not api_key or not uploaded_file,
            use_container_width=True
        )
        
        # AI Editing button (only show if we have chunks)
        if st.session_state.chunks and not st.session_state.editing_complete:
            st.divider()
            edit_with_ai = st.button(
                "✨ Edit with AI",
                type="secondary",
                disabled=st.session_state.processing,
                use_container_width=True,
                help="Use AI to enhance the writing style of your journal entries"
            )
        else:
            edit_with_ai = False
        
        # Retry AI editing button (if editing failed)
        if st.session_state.chunks and st.session_state.edited_chunks and not st.session_state.editing_complete:
            retry_editing = st.button(
                "🔄 Retry AI Editing",
                type="secondary",
                disabled=st.session_state.processing,
                use_container_width=True,
                help="Retry AI editing with your current settings"
            )
        else:
            retry_editing = False
        
        # Download PDF button (only show if editing is complete)
        if st.session_state.editing_complete and st.session_state.edited_chunks:
            st.divider()
            
            # Show PDF statistics
            pdf_stats = get_pdf_stats(st.session_state.edited_chunks)
            st.markdown("**📄 PDF Preview:**")
            st.markdown(f"• {pdf_stats['entries']} entries")
            st.markdown(f"• {pdf_stats['words']} words")
            st.markdown(f"• ~{pdf_stats['estimated_pages']} pages")
            
            # Generate PDF and download button
            try:
                pdf_bytes = create_pdf_bytes(st.session_state.edited_chunks, "Enhanced Journal")
                filename = get_pdf_filename(st.session_state.edited_chunks)
                
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    help="Download your enhanced journal as a professionally formatted PDF"
                )
                
            except Exception as e:
                st.error("❌ PDF generation failed")
                st.error(f"**Error details:** {str(e)}")
                st.error("**Possible solutions:**")
                st.error("• Try refreshing the page and clicking download again")
                st.error("• Check if your entries contain special characters that need formatting")
                st.info("💡 Your enhanced entries are preserved. The download will retry automatically when you click the button again.")
    
    # Main area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Status placeholder
        status_placeholder = st.empty()
        
        # Progress placeholder
        progress_placeholder = st.empty()
        
        if not st.session_state.processing:
            with status_placeholder.container():
                if not api_key:
                    st.info("👈 Please enter your OpenAI API key in the sidebar to get started")
                elif not uploaded_file:
                    st.info("👈 Please upload a document (PDF or DOCX) to begin processing")
                elif not st.session_state.chunks:
                    st.success("✅ Ready to process! Click 'Begin Processing' when ready.")
                elif not st.session_state.editing_complete:
                    st.info("📝 Document parsed successfully! Click '✨ Edit with AI' to enhance your writing.")
                # If editing is complete, the completion message is shown in results_placeholder
        
        # Results area 
        results_placeholder = st.empty()
        
        # Show final completion message if PDF is ready
        if st.session_state.editing_complete and st.session_state.edited_chunks:
            with results_placeholder.container():
                st.success("🎉 Your enhanced journal manuscript is ready!")
                
                # Show some completion stats
                editing_stats = get_editing_stats(st.session_state.edited_chunks)
                pdf_stats = get_pdf_stats(st.session_state.edited_chunks)
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Entries Enhanced", f"{editing_stats['successful']}/{editing_stats['total']}")
                with col_b:
                    st.metric("Total Words", pdf_stats['words'])
                with col_c:
                    st.metric("Estimated Pages", pdf_stats['estimated_pages'])
                
                st.markdown("---")
                st.markdown("**✨ Your writing has been enhanced with:**")
                st.markdown("• Improved rhythm and narrative flow")
                st.markdown("• Stronger verbs and vivid imagery")
                st.markdown("• Elimination of passive voice and unnecessary adverbs")
                st.markdown("• Professional prose style while preserving your authentic voice")
                
                st.info("📥 **Ready to download!** Use the 'Download PDF' button in the sidebar to get your polished manuscript.")
    
    with col2:
        st.subheader("Processing Info")
        info_placeholder = st.empty()
        
        if not st.session_state.processing:
            with info_placeholder.container():
                # Show chunk information if available
                if st.session_state.chunks:
                    st.markdown("**📊 Document Analysis:**")
                    chunk_summary = get_chunk_summary(st.session_state.chunks, method=st.session_state.chunking_method)
                    if st.session_state.chunking_method == "daily":
                        st.success(f"✅ Parsed: {chunk_summary}")
                    else:
                        st.success(f"✅ Split: {chunk_summary} ({st.session_state.paragraphs_per_chunk} paragraphs each)")
                    
                    # Show editing status if applicable
                    if st.session_state.editing_complete and st.session_state.edited_chunks:
                        editing_stats = get_editing_stats(st.session_state.edited_chunks)
                        st.success(f"🎨 AI Editing Complete: {editing_stats['successful']}/{editing_stats['total']} entries enhanced")
                    
                    # Show chunk details
                    chunks_to_show = st.session_state.edited_chunks if st.session_state.editing_complete else st.session_state.chunks
                    
                    if st.session_state.chunking_method == "daily":
                        expander_title = "View Entries"
                        chunk_label = "Day"
                    else:
                        expander_title = "View Chunks"
                        chunk_label = "Chunk"
                    
                    with st.expander(expander_title, expanded=False):
                        for chunk in chunks_to_show:
                            chunk_num = chunk['day']  # Actually chunk number for paragraph method
                            is_edited = chunk.get('edited', False) if st.session_state.editing_complete else False
                            
                            st.markdown(f"**{chunk_label} {chunk_num}** {'✨ (AI Enhanced)' if is_edited else ''}")
                            preview = chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                            st.text(preview)
                            st.divider()
                else:
                    st.markdown("""
                    **How it works:**
                    1. Upload your journal document
                    2. AI extracts and identifies day entries
                    3. Each entry is enhanced for style and flow
                    4. Download your polished manuscript as PDF
                    
                    **Supported formats:**
                    - PDF files
                    - Word documents (.docx)
                    """)
    
    # Handle processing
    if begin_processing:
        st.session_state.processing = True
        
        with status_placeholder.container():
            st.info("🚀 Processing started...")
        
        with progress_placeholder.container():
            progress_bar = st.progress(0, text="Initializing...")
        
        try:
            # Step 1: Extract text from document
            with status_placeholder.container():
                st.status("📄 Extracting text from document...", expanded=True)
            progress_bar.progress(20, text="📄 Extracting text from document...")
            
            file_bytes = uploaded_file.read()
            extracted_text, success, file_type = extract_document_text(file_bytes, uploaded_file.name)
            
            if not success:
                with status_placeholder.container():
                    st.error(f"❌ Failed to extract text from {file_type.upper()} document")
                    st.error("**Possible solutions:**")
                    st.error("• Ensure the document is not corrupted or password-protected")
                    st.error("• Try converting to a different format (PDF ↔ DOCX)")
                    st.error("• Check that the document contains readable text")
                    st.info("💡 Your API key and settings are preserved. Just upload a different document to try again.")
                st.session_state.processing = False
                st.rerun()
                return
            
            st.session_state.extracted_text = extracted_text
            
            # Step 2: Parse into chunks
            with status_placeholder.container():
                if st.session_state.chunking_method == "daily":
                    st.status("🔍 Parsing journal entries...", expanded=True)
                    progress_bar.progress(50, text="🔍 Parsing journal entries...")
                else:
                    st.status("🔍 Splitting into paragraph chunks...", expanded=True)
                    progress_bar.progress(50, text="🔍 Splitting into paragraph chunks...")
            
            chunks = chunk_document_text(
                extracted_text, 
                method=st.session_state.chunking_method,
                paragraphs_per_chunk=st.session_state.paragraphs_per_chunk
            )
            st.session_state.chunks = chunks
            
            chunk_count = get_chunk_count(chunks)
            
            if chunk_count == 0:
                with status_placeholder.container():
                    if st.session_state.chunking_method == "daily":
                        st.error("⚠️ No journal entries found in your document")
                        st.error("**Required format for daily journal entries:**")
                        st.error("• Each entry must start with 'Day 1', 'Day 2', etc.")
                        st.error("• Headers can have extra text: 'Day 1 - A Great Start'")
                        st.error("• Case doesn't matter: 'day 1' or 'DAY 1' work too")
                        st.info("💡 Try switching to 'By paragraph' chunking method, or upload a properly formatted document.")
                    else:
                        st.error("⚠️ No content chunks found in your document")
                        st.error("**Possible issues:**")
                        st.error("• Document may be too short or contain only whitespace")
                        st.error("• Try reducing the 'Paragraphs per chunk' setting")
                        st.error("• Switch to 'By daily journal entry' if your document has Day headers")
                        st.info("💡 Your settings are preserved. Try adjusting the chunking options or upload a different document.")
                st.session_state.processing = False
                st.rerun()
                return
            
            # Enhanced status message as specified in project plan
            with status_placeholder.container():
                if st.session_state.chunking_method == "daily":
                    st.status(f"Parsed ✓ — {chunk_count} entries", expanded=False, state="complete")
                    progress_bar.progress(75, text=f"✅ Found {chunk_count} journal entries")
                else:
                    st.status(f"Split ✓ — {chunk_count} chunks", expanded=False, state="complete")
                    progress_bar.progress(75, text=f"✅ Created {chunk_count} paragraph chunks")
            
            # Complete processing
            progress_bar.progress(100, text="🎉 Document parsed successfully!")
            
            with status_placeholder.container():
                chunk_summary = get_chunk_summary(chunks, method=st.session_state.chunking_method)
                st.success(f"✅ Processing complete! Parsed {chunk_summary}")
                if st.session_state.chunking_method == "daily":
                    st.info("👉 Review the entries in the sidebar, then click '✨ Edit with AI' to enhance your writing")
                else:
                    st.info("👉 Review the chunks in the sidebar, then click '✨ Edit with AI' to enhance your writing")
            
        except Exception as e:
            with status_placeholder.container():
                st.error("❌ Document processing failed")
                st.error(f"**Error details:** {str(e)}")
                st.error("**Possible solutions:**")
                st.error("• Check your internet connection")
                st.error("• Verify your document format is supported (PDF or DOCX)")
                st.error("• Try uploading a smaller document")
                st.info("💡 Your settings are preserved. You can upload a different document or try again.")
        
        finally:
            st.session_state.processing = False
            st.rerun()
    
    # Handle AI editing (both initial and retry)
    if edit_with_ai or retry_editing:
        st.session_state.processing = True
        
        with status_placeholder.container():
            st.info("🎨 Starting AI editing process...")
        
        with progress_placeholder.container():
            progress_bar = st.progress(0, text="Initializing AI editing...")
        
        try:
            # Define progress callback with enhanced status messages
            def update_progress(message):
                # Enhanced status messages as specified in project plan: "Sending batch 3/10 …"
                with status_placeholder.container():
                    st.status(message, expanded=False)
                
                if "batch" in message.lower():
                    # Extract batch info for progress calculation
                    if "batch " in message:
                        try:
                            parts = message.split("batch ")[1].split("/")
                            current_batch = int(parts[0])
                            total_batches = int(parts[1].split("...")[0])
                            progress_percent = int((current_batch / total_batches) * 80) + 10  # 10-90% range
                            progress_bar.progress(progress_percent, text=message)
                        except:
                            progress_bar.progress(50, text=message)
                    else:
                        progress_bar.progress(50, text=message)
            
            # Process chunks with AI editing
            with status_placeholder.container():
                st.status("🤖 Connecting to OpenAI...", expanded=True)
            progress_bar.progress(10, text="🤖 Connecting to OpenAI...")
            
            edited_chunks = process_chunks_in_batches(
                st.session_state.chunks,
                system_prompt=st.session_state.system_prompt,
                progress_callback=update_progress
            )
            
            st.session_state.edited_chunks = edited_chunks
            st.session_state.editing_complete = True
            
            # Enhanced completion status as specified: "Done — generating PDF"
            with status_placeholder.container():
                st.status("Done — generating PDF", expanded=False, state="complete")
            progress_bar.progress(100, text="🎉 AI editing complete!")
            
            # Display results
            editing_stats = get_editing_stats(edited_chunks)
            
            with status_placeholder.container():
                if editing_stats['failed'] == 0:
                    st.success(f"🎨 AI editing complete! Enhanced {editing_stats['successful']} journal entries")
                else:
                    st.warning(f"🎨 AI editing complete! Enhanced {editing_stats['successful']}/{editing_stats['total']} entries ({editing_stats['failed']} failed)")
                    if editing_stats['failed'] > 0:
                        st.error("**Some entries failed to process:**")
                        st.error("• This may be due to API rate limits or content issues")
                        st.error("• Failed entries will use their original text in the PDF")
                        st.info("💡 You can retry AI editing or download the PDF with partially enhanced content")
                    
                st.info("👉 Review the enhanced entries below, then use the '📥 Download PDF' button in the sidebar to get your polished manuscript")
            
        except Exception as e:
            with status_placeholder.container():
                st.error("❌ AI editing failed")
                st.error(f"**Error details:** {str(e)}")
                st.error("**Possible solutions:**")
                st.error("• Check your OpenAI API key is valid and has sufficient credits")
                st.error("• Verify your internet connection is stable")
                st.error("• Try simplifying your custom prompt if you modified it")
                st.error("• Wait a few minutes and try again (may be rate limited)")
                st.info("💡 Your parsed entries are preserved. You can retry editing or modify your prompt without re-uploading the document.")
        
        finally:
            st.session_state.processing = False
            st.rerun()

if __name__ == "__main__":
    main() 