import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import {
  GitPullRequest,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Brain,
  AlertCircle,
} from "lucide-react";

const StatusBadge = ({ status }) => {
  const statusConfig = {
    completed: { color: "bg-green-100 text-green-800", icon: CheckCircle },
    error: { color: "bg-red-100 text-red-800", icon: XCircle },
    mock: { color: "bg-yellow-100 text-yellow-800", icon: AlertCircle },
    not_analyzed: { color: "bg-gray-100 text-gray-800", icon: Clock },
  };

  const config = statusConfig[status] || statusConfig.not_analyzed;
  const Icon = config.icon;

  return (
    <span className={`status-badge ${config.color}`}>
      <Icon className="w-3 h-3 mr-1" />
      {status.replace("_", " ")}
    </span>
  );
};

const Dashboard = () => {
  const queryClient = useQueryClient();

  const {
    data: dashboard,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: api.getStats,
  });

  // Mutation for triggering analysis
  const analyzeMutation = useMutation({
    mutationFn: (prId) => api.triggerAnalysis(prId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-lg">
        <p className="text-red-800">Error loading dashboard: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total PRs</p>
              <p className="text-2xl font-bold">
                {dashboard?.data?.total_prs || 0}
              </p>
            </div>
            <GitPullRequest className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Analyzed</p>
              <p className="text-2xl font-bold">
                {dashboard?.data?.analyzed || 0}
              </p>
            </div>
            <Brain className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold">
                {dashboard?.data?.pending || 0}
              </p>
            </div>
            <Clock className="w-8 h-8 text-yellow-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">AI Enabled</p>
              <p className="text-2xl font-bold">
                {stats?.data?.ai_enabled ? "Yes" : "No"}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Pull Requests Table */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Recent Pull Requests</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PR
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Author
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Repository
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dashboard?.data?.pull_requests?.map((pr) => (
                <tr key={pr.pr_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{pr.pr_number}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="max-w-xs truncate">{pr.title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pr.author}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pr.repo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={pr.analysis_status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {pr.analysis_status === "not_analyzed" ? (
                      <button
                        onClick={() => analyzeMutation.mutate(pr.pr_id)}
                        disabled={analyzeMutation.isLoading}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {analyzeMutation.isLoading ? "Analyzing..." : "Analyze"}
                      </button>
                    ) : (
                      <Link
                        to={`/analysis/${pr.pr_id}`}
                        className="text-blue-600 hover:text-blue-800
                        font-medium"
                      >
                        View Analysis
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
