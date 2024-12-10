export default {
    data() {
        return {
        };
    },
    methods: {
        play(audio_player_id, track) {
            const audio_player = document.getElementById(audio_player_id)
            const media_src = new MediaSource()
            audio_player.src = URL.createObjectURL(media_src);

            media_src.addEventListener("sourceopen", () => {
                const source = media_src.addSourceBuffer("audio/mp4; codecs=\"mp4a.40.2\"")
                let chunks = []
                let playing = false;
                
                const process_chunks = () => {
                    if (!source || !source.appendBuffer) {
                        return;
                    }
                    if (chunks.length > 0 && !source.updating) {
                        console.log("Appending a chunk for playback...")
                        const chunk = chunks.shift();
                        source.appendBuffer(chunk);
                        if (!playing) {
                            console.log("Starting playback.")
                            audio_player.play();
                            playing = true;
                        }
                    }
                }
                
                source.addEventListener("updateend", process_chunks);
                const ws_url = "ws://192.168.29.35:8765";
                const ws = new WebSocket(ws_url);
                ws.binaryType = "arraybuffer";

                ws.onopen = () => {
                    ws.send(JSON.stringify({from: "track", track: track}))
                }
                
                ws.onmessage = (event) => {
                    chunks.push(new Uint8Array(event.data))
                    process_chunks()
                }
            })
        }
    },
    props: {
    },
};
