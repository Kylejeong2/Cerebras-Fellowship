# Cerebras AI Phone Agent

`Summary of what you built`

1. I built AI RAG phone agents using Deepgram STT, Cerebras inference with Llama 3.1 8b, and Cartesia TTS. The RAG pipeline is through pinecone, using their vector database as well as query API, and embeddings are done by OpenAI (text-embedding-small). Telephony is through Twilio. You can upload a document to the Agent which is embedded and then referenced through RAG when speaking to the agent. Also I built a Google Calendar integration which can check my calendar for availability and book times based on that. 

`How you built it`

1. Using the livekit agent SDK, I utilized the Cartesia and Deepgram STT & TTS models right out of the box, and wrote my own custom service to use Cerebras inference for the LLM layer. The custom service queries Cerebras’ super fast inference with llama 3.1 8b model (lower params for lower latency), and sequentially processes it through text-to-speech through the phone. I also wrote the RAG class and query functions in python to allow the agent to retrieve information from pinecone when needed. 

`How your project leverages Cerebras' fast inference`

1. My project uses Cerebras’ fast inference to reduce latency over Voice AI applications. Creating good AI Voice is tough, you want high quality and reliable responses, but also need extremely low latency or the conversation doesn’t sound/feel normal. Cerebras’ inference is almost instant, which allows the LLM part of the voice pipeline to be as optimized as possible for lowest total latency. 

`How you plan to continue working on the project and future roadmap`

1. I’m planning to continue working on this, looking to help small business owners around America have their own AI phone agent to book more appointments/revenue, keep their customers happy around the clock, and even save more money by not having to hire another employee. I’m close to official launch with 2 small businesses currently on the waitlist ready to use the product. In the next 3-5 years, every small business will have an AI agent. Don’t believe me? [Here’s some market validation from Mark Zuckerberg](https://www.youtube.com/watch?v=kKm_0eLmbzQ).

Here’s the link to the [Demo](https://www.loom.com/share/d071dd02e96a418e96236ec55fbe5171?sid=9b640a62-707b-488e-a08e-14cab57a8f67).

Here’s a link to the [Github Project](https://github.com/Kylejeong2/Cerebras-Fellowship).

Thanks Cerebras for letting me try your instant inference?

-Kyle Jeong