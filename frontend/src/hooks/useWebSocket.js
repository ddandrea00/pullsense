import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);
  const queryClient = useQueryClient();
  const reconnectTimeoutRef = useRef(null);

  const connect = () => {
    try {
      const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log("✅ WebSocket connected");
        setIsConnected(true);

        // Clear any reconnect timeout
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log("📨 WebSocket message:", message);

          // Handle different message types
          switch (message.type) {
            case "pr_created":
              // Invalidate dashboard to fetch new PR
              queryClient.invalidateQueries({ queryKey: ["dashboard"] });
              break;

            case "analysis_complete":
              // Invalidate specific queries
              queryClient.invalidateQueries({ queryKey: ["dashboard"] });
              queryClient.invalidateQueries({
                queryKey: ["analysis", message.data.pr_id.toString()],
              });
              break;

            default:
              console.log("Unknown message type:", message.type);
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.current.onclose = () => {
        console.log("🔌 WebSocket disconnected");
        setIsConnected(false);

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log("🔄 Attempting to reconnect...");
          connect();
        }, 3000);
      };

      ws.current.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
      };
    } catch (error) {
      console.error("❌ Failed to create WebSocket connection:", error);
    }
  };

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  return { isConnected };
};
