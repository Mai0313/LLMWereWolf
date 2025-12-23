import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useGameEvents, useAutoScroll } from "@store/gameStore";
import { GameEvent } from "@/types/game";
import { DownOutlined } from "@ant-design/icons";

const EventItem: React.FC<{ event: GameEvent }> = ({ event }) => {
  const getStyle = () => {
    switch (event.type) {
      case "PLAYER_DIED":
        return { border: "border-mystic-blood", bg: "bg-mystic-blood/5", icon: "💀" };
      case "ROLE_ACTION":
        return { border: "border-mystic-accent", bg: "bg-mystic-accent/5", icon: "✨" };
      case "VOTING":
        return { border: "border-mystic-gold", bg: "bg-mystic-gold/5", icon: "🗳️" };
      case "DISCUSSION":
        return { border: "border-gray-700", bg: "bg-transparent", icon: "💬" };
      default:
        return { border: "border-gray-800", bg: "bg-transparent", icon: "ℹ️" };
    }
  };

  const style = getStyle();

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`
        mb-3 p-3 rounded-r-lg border-l-2 ${style.border} 
        ${style.bg} hover:bg-white/5 transition-colors duration-300
      `}
    >
      <div className="flex justify-between items-center mb-1 text-[10px] text-gray-500 tracking-wider font-mono">
        <span className="flex items-center gap-1">
          <span>{style.icon}</span>
          <span>R{event.round}</span>
        </span>
        <span>{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
      </div>
      <div className="text-sm text-gray-300 font-light leading-relaxed font-sans">
        {event.message}
      </div>
    </motion.div>
  );
};

const EventFeed: React.FC = () => {
  const events = useGameEvents();
  const autoScroll = useAutoScroll();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events, autoScroll]);

  return (
    <div className="h-full flex flex-col relative overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-white/5 bg-black/20 backdrop-blur-sm z-10">
        <h3 className="font-serif text-mystic-text tracking-[0.2em] text-sm uppercase m-0 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-mystic-accent rounded-full animate-pulse"></span>
          Chronicles
        </h3>
      </div>

      {/* Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-1 scrollbar-hide mask-image-gradient">
        <AnimatePresence>
          {events.length === 0 && (
            <div className="h-full flex items-center justify-center text-gray-600 font-serif italic text-sm">
              Waiting for the night to fall...
            </div>
          )}
          {events.map((event) => (
            <EventItem key={event.id} event={event} />
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Auto-scroll indicator */}
      {autoScroll && events.length > 5 && (
        <div className="absolute bottom-4 right-4 z-20 text-mystic-accent animate-bounce opacity-50">
          <DownOutlined />
        </div>
      )}
    </div>
  );
};

export default EventFeed;