import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import {
  ArrowLeft,
  Brain,
  Clock,
  CheckCircle,
  AlertTriangle,
  GitPullRequest,
  User,
  Calendar,
  Zap,
} from "lucide-react";

const AnalysisDetail = () => {
  const { prId } = useParams();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ["analysis", prId],
    queryFn: () => api.getPullRequestAnalysis(prId),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Brain className="w-8 h-8 animate-pulse text-blue-600" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 p-4 rounded-lg">
        <p className="text-red-800">Error loading analysis</p>
      </div>
    );
  }

  const pr = data.data.pull_request;
  const analysis = data.data.analysis;

  // Parse the analysis text to extract sections if it's structured
  const renderAnalysisText = (text) => {
    // Split by newlines and render with proper formatting
    return text.split("\n").map((line, index) => {
      // Check if it's a heading (starts with number and dot)
      if (/^\d+\./.test(line)) {
        return (
          <h3 key={index} className="font-semibold mt-4 mb-2">
            {line}
          </h3>
        );
      }
      // Check if it's a bullet point
      if (line.trim().startsWith("-")) {
        return (
          <li key={index} className="ml-4">
            {line.substring(1).trim()}
          </li>
        );
      }
      // Regular paragraph
      if (line.trim()) {
        return (
          <p key={index} className="mb-2">
            {line}
          </p>
        );
      }
      return null;
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "mock":
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Back Button */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </button>

      {/* PR Header */}
      <div className="card mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center mb-2">
              <GitPullRequest className="w-6 h-6 text-blue-600 mr-2" />
              <h1 className="text-2xl font-bold">PR #{pr.number}</h1>
            </div>
            <h2 className="text-lg text-gray-700 mb-4">{pr.title}</h2>

            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <div className="flex items-center">
                <User className="w-4 h-4 mr-1" />
                {pr.author}
              </div>
              <div className="flex items-center">
                {getStatusIcon(analysis.status)}
                <span className="ml-1">{analysis.status}</span>
              </div>
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {analysis.analysis_time?.toFixed(2)}s
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Content */}
      <div className="card">
        <div className="flex items-center mb-4">
          <Brain className="w-6 h-6 text-blue-600 mr-2" />
          <h2 className="text-xl font-semibold">AI Analysis</h2>
        </div>

        {/* Model Info */}
        <div className="bg-blue-50 text-blue-800 px-4 py-2 rounded-lg mb-6 flex items-center">
          <Zap className="w-4 h-4 mr-2" />
          <span className="text-sm">
            Analyzed using {analysis.model} on{" "}
            {new Date(analysis.created_at).toLocaleDateString()}
          </span>
        </div>

        {/* Analysis Text */}
        <div className="prose prose-gray max-w-none">
          {renderAnalysisText(analysis.text)}
        </div>
      </div>
    </div>
  );
};

export default AnalysisDetail;
