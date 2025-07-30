import streamlit as st
from utils.youtube import download_youtube_video, fetch_youtube_meta
from utils.instagram import post_on_insta
from utils.caption import generate_caption
from utils.file_handler import delete_video_file
from utils.youtube_search import search_youtube
from config import GROQ_API_KEY, ACCOUNTS


def process_single_url(url, selected_account):
    insta_user = selected_account["username"]
    insta_pass = selected_account["password"]
    custom_prompt = selected_account["prompt"]

    try:
        st.info(f"📥 Downloading video: {url}")
        video_path = download_youtube_video(url)

        st.info(f"🔍 Fetching metadata for: {url}")
        title, description = fetch_youtube_meta(url)

        st.info(f"🧠 Generating caption for: {url}")
        caption = generate_caption(title, description, custom_prompt)

        st.info(f"📤 Posting to Instagram: {url}")
        result, error = post_on_insta(video_path, caption, insta_user, insta_pass)

        if result:
            st.success(f"✅ Successfully posted: {url}")
            delete_video_file(video_path)
        else:
            st.error(f"❌ Failed to post {url}: {error}")
    except Exception as e:
        st.error(f"An error occurred while processing {url}: {str(e)}")


def process_queue(url_queue, selected_account):
    if not url_queue:
        st.warning("Queue is empty. Add URLs to the queue first.")
        return

    st.subheader("🚀 Starting Auto-Post Process")
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_urls = len(url_queue)
    for i, url in enumerate(url_queue):
        status_text.write(f"Processing URL {i + 1}/{total_urls}: {url}")
        with st.spinner(f"Processing {url}..."):
            process_single_url(url, selected_account)
        progress_bar.progress((i + 1) / total_urls)

    st.success("🎉 Auto-post process completed!")
    st.session_state.url_queue = []  


def run_ui():
    st.set_page_config(page_title="YouTube to Instagram Poster", page_icon="📹")

    st.title("📹 YouTube to Instagram Poster")
    st.markdown(
        "Download YouTube Shorts and post them to Instagram with AI-generated captions"
    )

    if "url_queue" not in st.session_state:
        st.session_state.url_queue = []
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "current_search_index" not in st.session_state:
        st.session_state.current_search_index = 0

    with st.expander("🔑 API Configuration"):
        try:
            default_groq = st.secrets.get("GROQ_API_KEY", "")
        except:
            default_groq = GROQ_API_KEY

        groq_key = st.text_input("Groq API Key", type="password", value=default_groq)

        account_names = [account["username"] for account in ACCOUNTS]
        selected_account_name = st.selectbox("Select Instagram Account", account_names)
        selected_account = next((acc for acc in ACCOUNTS if acc["username"] == selected_account_name), None)

    st.markdown("---")
    st.subheader("🔎 YouTube Search and Preview")
    search_query = st.text_input("Enter search query (e.g., 'funny cat videos')")
    col_k, col_type = st.columns(2)
    with col_k:
        k_results = st.number_input("Number of results (k)", min_value=1, max_value=20, value=5)
    with col_type:
        video_type = st.radio("Video Type", ('all', 'videos', 'shorts'))

    if st.button("Search YouTube"):
        if not search_query:
            st.warning("Please enter a search query.")
        else:
            with st.spinner(f"Searching YouTube for '{search_query}'..."):
                results = search_youtube(search_query, k_results, video_type)
                if results:
                    st.session_state.search_results = results
                    st.session_state.current_search_index = 0
                    st.success(f"Found {len(results)} results.")
                else:
                    st.warning("No results found for your query.")
                    st.session_state.search_results = []
                    st.session_state.current_search_index = 0

    if st.session_state.search_results:
        st.markdown("### Preview and Decide")
        if st.session_state.current_search_index < len(st.session_state.search_results):
            current_result = st.session_state.search_results[st.session_state.current_search_index]
            st.write(f"**Title:** {current_result['title']}")
            st.video(current_result['url'])

            col_approve, col_skip = st.columns(2)
            with col_approve:
                if st.button("👍 Approve and Add to Queue"):
                    if not selected_account:
                        st.error("Please select an Instagram account before adding to queue.")
                    elif not groq_key:
                        st.error("Please provide a Groq API key before adding to queue.")
                    else:
                        st.session_state.url_queue.append(current_result['url'])
                        st.success(f"Added '{current_result['title']}' to the queue.")
                        st.session_state.current_search_index += 1
                        st.rerun()
            with col_skip:
                if st.button("⏭️ Skip"):
                    st.session_state.current_search_index += 1
                    st.rerun()
        else:
            st.info("All search results have been processed.")
            st.session_state.search_results = []
            st.session_state.current_search_index = 0

    st.markdown("---")
    st.subheader("📝 Manual URL Queue")
    queue_urls_input = st.text_area(
        "Enter YouTube Shorts URLs (one per line)", height=150
    )
    col_queue1, col_queue2 = st.columns(2)
    with col_queue1:
        if st.button("➕ Add to Queue"):
            new_urls = [url.strip() for url in queue_urls_input.split("\n") if url.strip()]
            if new_urls:
                st.session_state.url_queue.extend(new_urls)
                st.success(f"Added {len(new_urls)} URL(s) to the queue.")
            else:
                st.warning("No URLs entered to add to queue.")
    with col_queue2:
        if st.button("🧹 Clear Queue"):
            st.session_state.url_queue = []
            st.info("Queue cleared.")

    if st.session_state.url_queue:
        st.write("**Current Queue:**")
        for i, q_url in enumerate(st.session_state.url_queue):
            st.write(f"{i+1}. {q_url}")

        if st.button("▶️ Start Auto-Post"):
            if not selected_account:
                st.error("Please select an Instagram account.")
            elif not groq_key:
                st.error("Please provide a Groq API key to start auto-post.")
            else:
                process_queue(st.session_state.url_queue, selected_account)
    else:
        st.info("Queue is empty.")

    st.markdown("---")
    st.caption(
        "Made with Streamlit | Ensure your Instagram account allows API access"
    )