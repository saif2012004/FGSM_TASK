"use client";

import { useState, useRef } from "react";
import Image from "next/image";

interface AttackResult {
  clean_prediction: number;
  adversarial_prediction: number;
  adversarial_image: string;
  attack_success: boolean;
  confidence_clean: number;
  confidence_adversarial: number;
  epsilon_used: number;
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [epsilon, setEpsilon] = useState<number>(0.1);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AttackResult | null>(null);
  const [error, setError] = useState<string>("");
  const [originalImageUrl, setOriginalImageUrl] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Backend URL - change this for deployment
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError("");
      setResult(null);

      // Create preview URL for original image
      const url = URL.createObjectURL(file);
      setOriginalImageUrl(url);
    }
  };

  const handleEpsilonChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEpsilon(parseFloat(event.target.value));
  };

  const runAttack = async () => {
    if (!selectedFile) {
      setError("Please select an image file first");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("epsilon", epsilon.toString());

      console.log("🚀 Making API call to:", `${API_BASE_URL}/attack`);

      const response = await fetch(`${API_BASE_URL}/attack`, {
        method: "POST",
        body: formData,
      });

      console.log("📥 Response status:", response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ API Response:", data);
      setResult(data);
    } catch (err) {
      console.error("❌ Attack failed:", err);
      if (err instanceof Error) {
        if (err.message.includes("fetch")) {
          setError(
            "Network error: Unable to connect to the server. Make sure the backend is running."
          );
        } else {
          setError(`Request error: ${err.message}`);
        }
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  const resetDemo = () => {
    setSelectedFile(null);
    setResult(null);
    setError("");
    setOriginalImageUrl("");
    setEpsilon(0.1);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const getDigitName = (digit: number): string => {
    const names = [
      "Zero",
      "One",
      "Two",
      "Three",
      "Four",
      "Five",
      "Six",
      "Seven",
      "Eight",
      "Nine",
    ];
    return names[digit] || `Digit ${digit}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            FGSM Adversarial Attack Demo
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Upload an image and see how the Fast Gradient Sign Method (FGSM) can
            create adversarial examples that fool machine learning models.
            Adjust the epsilon parameter to control the attack strength.
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          {/* Upload Section */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              1. Upload Image
            </h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
              >
                {selectedFile ? "Change Image" : "Select Image"}
              </label>
              {selectedFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {selectedFile.name}
                </p>
              )}
            </div>
          </div>

          {/* Epsilon Control */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              2. Set Attack Strength (Epsilon)
            </h2>
            <div className="flex items-center space-x-4">
              <label
                htmlFor="epsilon"
                className="text-sm font-medium text-gray-700"
              >
                Epsilon:
              </label>
              <input
                type="range"
                id="epsilon"
                min="0"
                max="1.0"
                step="0.01"
                value={epsilon}
                onChange={handleEpsilonChange}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-sm font-medium text-gray-700 min-w-[60px]">
                {epsilon.toFixed(2)}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Higher epsilon values create stronger attacks but more visible
              perturbations (0.0-1.0 range)
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 mb-8">
            <button
              onClick={runAttack}
              disabled={!selectedFile || loading}
              className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {loading ? "Generating Attack..." : "Run FGSM Attack"}
            </button>
            <button
              onClick={resetDemo}
              className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Reset
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold text-gray-800">
                3. Attack Results
              </h2>

              {/* Attack Summary */}
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div
                      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                        result.attack_success
                          ? "bg-red-100 text-red-800"
                          : "bg-green-100 text-green-800"
                      }`}
                    >
                      {result.attack_success
                        ? "🔴 Attack Successful"
                        : "🟢 Attack Failed"}
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Epsilon Used</p>
                    <p className="text-lg font-semibold">
                      {result.epsilon_used.toFixed(2)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Prediction Changed</p>
                    <p className="text-lg font-semibold">
                      {result.clean_prediction} →{" "}
                      {result.adversarial_prediction}
                    </p>
                  </div>
                </div>
              </div>

              {/* Image Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Original Image */}
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Original Image
                  </h3>
                  {originalImageUrl && (
                    <div className="relative inline-block">
                      <Image
                        src={originalImageUrl}
                        alt="Original"
                        width={200}
                        height={200}
                        className="border border-gray-300 rounded-lg object-cover"
                        style={{ width: "auto", height: "200px" }}
                      />
                    </div>
                  )}
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <p className="font-semibold text-blue-800">
                      Prediction: {getDigitName(result.clean_prediction)}
                    </p>
                    <p className="text-sm text-blue-600">
                      Confidence: {(result.confidence_clean * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Adversarial Image */}
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Adversarial Image
                  </h3>
                  <div className="relative inline-block">
                    <Image
                      src={`data:image/png;base64,${result.adversarial_image}`}
                      alt="Adversarial"
                      width={200}
                      height={200}
                      className="border border-gray-300 rounded-lg object-cover"
                      style={{ width: "auto", height: "200px" }}
                    />
                  </div>
                  <div className="mt-4 p-4 bg-red-50 rounded-lg">
                    <p className="font-semibold text-red-800">
                      Prediction: {getDigitName(result.adversarial_prediction)}
                    </p>
                    <p className="text-sm text-red-600">
                      Confidence:{" "}
                      {(result.confidence_adversarial * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Explanation */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h4 className="font-semibold text-blue-900 mb-2">
                  What happened?
                </h4>
                <p className="text-blue-800 text-sm">
                  {result.attack_success ? (
                    <>
                      The FGSM attack successfully fooled the model! By adding
                      carefully crafted noise (epsilon ={" "}
                      {result.epsilon_used.toFixed(2)}) to the original image,
                      we changed the model&apos;s prediction from &quot;
                      {getDigitName(result.clean_prediction)}&quot; to &quot;
                      {getDigitName(result.adversarial_prediction)}&quot; while
                      the image looks nearly identical to human eyes.
                    </>
                  ) : (
                    <>
                      The FGSM attack did not change the model&apos;s
                      prediction. The model still predicts &quot;
                      {getDigitName(result.clean_prediction)}&quot; even after
                      adding adversarial noise. Try increasing the epsilon value
                      for a stronger attack.
                    </>
                  )}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Information Section */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            About FGSM
          </h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 mb-4">
              The Fast Gradient Sign Method (FGSM) is a simple yet effective
              adversarial attack technique introduced by Goodfellow et al. It
              generates adversarial examples by taking a step in the direction
              of the gradient of the loss function with respect to the input
              image.
            </p>
            <p className="text-gray-600 mb-4">
              The mathematical formulation is:{" "}
              <strong>x_adv = x + ε × sign(∇_x J(θ, x, y))</strong>
            </p>
            <p className="text-gray-600">
              Where ε (epsilon) controls the magnitude of the perturbation, and
              the attack becomes stronger as epsilon increases, but the changes
              become more visible to humans.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>DevNeuron Internship Assessment - Software Engineer Position</p>
        </div>
      </div>
    </div>
  );
}
