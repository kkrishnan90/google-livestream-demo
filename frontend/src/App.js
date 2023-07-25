import "./App.css";
import Home from "./components/home";
const BG_URL =
  "https://i.pinimg.com/originals/6a/00/92/6a009257f2f7b6a6fd62b9f63a849168.jpg";
function App() {
  return (
    <div
      className="App h-screen text-start space-y-4 py-4 bg-black px-4 overflow-y-scroll"
      style={{ backgroundImage: "url(" + BG_URL + ")" }}
    >
      <h1 className="text-3xl font-bold text-amber-500">Live Stream Demo</h1>
      <Home />
    </div>
  );
}

export default App;
