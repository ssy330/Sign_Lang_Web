import React, { useState } from "react";

const ClearableTextBox = ({ initialText = "", onRemove }) => {
  const [text, setText] = useState(initialText);

  const handleRemove = () => {
    if (onRemove) onRemove(); // 부모 컴포넌트에 삭제 요청
  };

  return (
    <div style={styles.container}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={styles.textBox}
        placeholder="Type something..."
      />
      <button onClick={handleRemove} style={styles.clearButton}>
        ×
      </button>
    </div>
  );
};

const styles = {
  container: {
    position: "relative",
    display: "inline-block",
    width: "700px",
    marginBottom: "10px", // 텍스트 박스 간 간격
  },
  textBox: {
    width: "100%",
    padding: "8px",
    paddingRight: "30px",
    boxSizing: "border-box",
  },
  clearButton: {
    position: "absolute",
    top: "50%",
    right: "8px",
    transform: "translateY(-50%)",
    border: "none",
    background: "none",
    cursor: "pointer",
    fontSize: "16px",
    color: "#888",
  },
};

export default ClearableTextBox;
