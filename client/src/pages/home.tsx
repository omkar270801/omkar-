import { useState } from "react";
import { Shield, Settings, Cog, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import UploadZone from "@/components/upload-zone";
import ImageAnalysis from "@/components/image-analysis";
import ResultsPanel from "@/components/results-panel";
import ProcessingModal from "@/components/processing-modal";
import AdvancedSettings from "@/components/advanced-settings";
import TrainingPanel from "@/components/training-panel";
import type { AnalysisResponse } from "@shared/schema";
import axios from "axios";

export default function Home() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [showTrainingPanel, setShowTrainingPanel] = useState(false);

  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    setAnalysisResult(null);
    
    // Create image preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleAnalysisResult = (result: AnalysisResponse) => {
    setAnalysisResult(result);
    setIsProcessing(false);
  };

  const handleProcessingStart = () => {
    setIsProcessing(true);
  };

  const handleNewAnalysis = () => {
    setUploadedFile(null);
    setAnalysisResult(null);
    setImagePreview(null);
    setIsProcessing(false);
  };

  // Add handler for training image upload and backend trigger
  const handleTrainModel = async (files: File[]) => {
    if (!files || files.length === 0) return;
    const formData = new FormData();
    files.forEach((file, idx) => {
      formData.append("images", file);
    });
    try {
      // POST to backend training endpoint
      await axios.post("/api/train", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("Training started successfully!");
    } catch (err) {
      alert("Training failed. Please try again.");
    }
  };

  return (
    <div className="bg-background-light min-h-screen">
      {/* Header */}
      <header className="bg-surface elevation-1 border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-3">
                <img src="/logo.png" alt="Logo" className="w-12 h-12 object-contain" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">MDL WELDX</h1>
                <p className="text-sm text-muted-foreground">(AI Welding X-Ray Defect detection System)</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-muted-foreground flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
               AI Model 1.0
              </div>
              <Button 
                variant="outline" 
                className="border-orange-200 text-orange-700 hover:bg-orange-50"
                onClick={() => setShowTrainingPanel(true)}
              >
                <GraduationCap className="mr-2 w-4 h-4" />
                Train Model
              </Button>
              {/* <Button 
                variant="outline" 
                className="border-primary text-primary hover:bg-primary hover:text-primary-foreground"
                onClick={() => setShowAdvancedSettings(true)}
              >
                <Cog className="mr-2 w-4 h-4" />
                Advanced
              </Button> */}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload and Analysis Section */}
          <div className="lg:col-span-2 space-y-6">
            <UploadZone 
              onFileUpload={handleFileUpload}
              onProcessingStart={handleProcessingStart}
            />
            
            {imagePreview && (
              <ImageAnalysis
                imagePreview={imagePreview}
                analysisResult={analysisResult}
                isProcessing={isProcessing}
              />
            )}
          </div>

          {/* Results Panel */}
          <div className="space-y-6">
            <ResultsPanel 
              analysisResult={analysisResult}
              onNewAnalysis={handleNewAnalysis}
            />
          </div>
        </div>
      </main>

      {/* Processing Modal */}
      <ProcessingModal 
        isOpen={isProcessing}
        onAnalysisComplete={handleAnalysisResult}
        uploadedFile={uploadedFile}
      />

      {/* Advanced Settings Modal */}
      <AdvancedSettings
        isOpen={showAdvancedSettings}
        onClose={() => setShowAdvancedSettings(false)}
      />

      {/* Training Panel Modal */}
      <TrainingPanel
        isOpen={showTrainingPanel}
        onClose={() => setShowTrainingPanel(false)}
        onTrainModel={handleTrainModel} // <-- pass handler as prop
      />
    </div>
  );
}
