import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import ClearableTextBox from './components/ClearableTextBox';
import './App.css'; // CSS 파일 추가

function App() {
  const [sentence, setSentence] = useState(""); // 기존 텍스트 박스 상태
  const [textBoxes, setTextBoxes] = useState([]); // 텍스트 박스 배열 상태

  useEffect(() => {
    const socket = io("http://127.0.0.1:5000");

    socket.on("sentence_update", (data) => {
      setSentence(data.sentence);
    });

    socket.on("add_textbox", (data) => {
      setTextBoxes((prev) => [
        ...prev,
        { id: Date.now(), content: data.content }, // 텍스트 박스에 고유 ID 추가
      ]);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleRemoveTextBox = (id) => {
    setTextBoxes((prev) => prev.filter((box) => box.id !== id));
  };

  return (
    <div className="container">
      <div className="top-input">
        <h1>수화 실시간 번역</h1>
      </div>

      <div className="main-content">
        <div className="streaming">
          <img
            src="http://localhost:5000/video_feed"
            alt="Video Stream"
          />
          <input
            type="text"
            value={sentence}
            autoFocus
          />
        </div>

        <div className="textbox-container">
          {textBoxes.map((box) => (
            <ClearableTextBox
              key={box.id}
              initialText={box.content}
              onRemove={() => handleRemoveTextBox(box.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
