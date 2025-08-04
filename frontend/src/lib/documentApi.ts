/**
 * Document Processing API Integration
 * 
 * This module provides functions to communicate with the document processing backend
 */

const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface DocumentProcessingResult {
  file_name: string;
  status: 'success' | 'failed' | 'error';
  error?: string;
  output_file?: string;
}

export interface VectorStorageResult {
  status: 'success' | 'error' | 'skipped';
  total_segments?: number;
  successful_vectors?: number;
  failed_vectors?: number;
  total_upserted?: number;
  method?: string;
  index_stats?: {
    total_vector_count: number;
    dimension: number;
    index_fullness: number;
  };
  error?: string;
  reason?: string;
}

export interface BulkProcessResponse {
  message: string;
  total_files: number;
  successful: number;
  failed: number;
  output_directory: string;
  timestamp: string;
  results: DocumentProcessingResult[];
  vector_storage: VectorStorageResult[];
}

export interface DocumentUploadProgress {
  stage: 'uploading' | 'processing' | 'ocr' | 'vector' | 'completed' | 'error';
  progress: number;
  message: string;
  details?: any;
}

/**
 * Upload and process documents using the bulk processing endpoint
 */
export async function uploadAndProcessDocuments(
  files: File[],
  outputDir?: string,
  onProgress?: (progress: DocumentUploadProgress) => void
): Promise<BulkProcessResponse> {
  try {
    // Stage 1: Uploading
    onProgress?.({
      stage: 'uploading',
      progress: 0,
      message: `Uploading ${files.length} file${files.length > 1 ? 's' : ''}...`
    });

    // Create FormData for file upload
    const formData = new FormData();
    
    // Add files to FormData
    files.forEach(file => {
      formData.append('files', file);
    });
    
    // Add optional output directory
    if (outputDir) {
      formData.append('output_dir', outputDir);
    }

    // Stage 2: Processing
    onProgress?.({
      stage: 'processing',
      progress: 25,
      message: 'Processing documents with Chunkr AI...'
    });

    // Make API call to backend
    const response = await fetch(`${BACKEND_BASE_URL}/api/documents/bulk-process`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Stage 3: OCR (included in processing)
    onProgress?.({
      stage: 'ocr',
      progress: 50,
      message: 'Extracting data with advanced OCR...'
    });

    const data: BulkProcessResponse = await response.json();

    // Stage 4: Vector storage
    onProgress?.({
      stage: 'vector',
      progress: 75,
      message: 'Storing documents in vector database...'
    });

    // Stage 5: Completed
    onProgress?.({
      stage: 'completed',
      progress: 100,
      message: 'Processing completed successfully!',
      details: data
    });

    return data;

  } catch (error) {
    console.error('Error uploading and processing documents:', error);
    
    onProgress?.({
      stage: 'error',
      progress: 0,
      message: `Error processing documents: ${error}`,
      details: { error }
    });

    throw new Error(`Failed to process documents: ${error}`);
  }
}

/**
 * Check if the backend service is healthy
 */
export async function checkBackendHealth(): Promise<{ status: string; timestamp: string; version: string } | null> {
  try {
    const response = await fetch(`${BACKEND_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error checking backend health:', error);
    return null;
  }
}

/**
 * Process existing JSON files in a directory and store in Pinecone
 */
export async function processExistingJsonFiles(
  jsonDir?: string
): Promise<{ message: string; total_files: number; successful_storage: number; failed_storage: number; total_vectors_stored: number }> {
  try {
    const response = await fetch(`${BACKEND_BASE_URL}/api/vectors/store-existing-json`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ json_dir: jsonDir || 'processed' }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error processing existing JSON files:', error);
    throw new Error(`Failed to process existing JSON files: ${error}`);
  }
}