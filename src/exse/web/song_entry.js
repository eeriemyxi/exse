export default {
    template: `
    <button @click="handle_click" style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #1d2021;
    color: #ebdbb2;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    font-family: Arial, sans-serif;
    cursor: pointer;
    width: 100%;
    transition: background-color 0.3s ease;"
    onmouseover="this.style.backgroundColor='#3c3836';"
    onmouseout="this.style.backgroundColor='#1d2021';"
    onmousedown="this.style.backgroundColor='#665c54';"
    onmouseup="this.style.backgroundColor='#3c3836';">
    <div style="font-weight: bold; font-size: 1.1em;">{{title}}</div>
    <div style="font-size: 0.9em; color: #8a7d6c; text-align: right;">{{artist}}</div>
    </button>
    `,
    data() {
        return {
        };
    },
    methods: {
        handle_click() {
            this.$emit("click")
        }
    },
    props: {
        title: String,
        artist: String
    },
};
