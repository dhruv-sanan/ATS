"use client";

import { EventLog } from "@/components/EventLog";
import { EmailLog } from "@/components/EmailLog";
import axios from "axios";
import InputSection from "@/components/InputSection";
import { useCrewJob } from "@/hooks/useCrewJob";
import { FileState, MultiFileDropzone } from "@/components/FileUploader";
import { useState } from "react";
import { useEdgeStore } from '@/lib/edgestore';
import React from "react";

export default function Home() {
  // Hooks
  const crewJob = useCrewJob();
  const [fileStates, setFileStates] = useState<FileState[]>([]);
  const { edgestore } = useEdgeStore();
  const [urls, setUrls] = useState<string[]>([]);
  

  const [uploadRes, setUploadRes] = useState<
    {
      url: string;
      filename: string;
    }[]
  >([]);

  // function updateFileProgress(key: string, progress: FileState['progress']) {
  //   setFileStates((fileStates) => {
  //     const newFileStates = structuredClone(fileStates);
  //     const fileState = newFileStates.find(
  //       (fileState) => fileState.key === key,
  //     );
  //     if (fileState) {
  //       fileState.progress = progress;
  //     }
  //     return newFileStates;
  //   });
  // }
  // const handleFileAdded = async (addedFiles) => {
  //   setFileStates([...fileStates, ...addedFiles]);
  //   await Promise.all(
  //     addedFiles.map(async (addedFileState) => {
  //       try {
  //         const res = await edgestore.myPublicFiles.upload({
  //           file: addedFileState.file,
  //           onProgressChange: async (progress) => {
  //             updateFileProgress(addedFileState.key, progress);
  //             if (progress === 100) {
  //               // wait 1 second to set it to complete
  //               // so that the user can see the progress bar at 100%
  //               await new Promise((resolve) => setTimeout(resolve, 1000));
  //               updateFileProgress(addedFileState.key, 'COMPLETE');
  //             }
  //           },
  //         });
  //         extractText(res.url)
  //         setUrls([...urls, res.url]);
  //         console.log(res);
  //       } catch (err) {
  //         updateFileProgress(addedFileState.key, 'ERROR');
  //       }
  //     }),
  //   )}

    
  return (
    <div className="bg-white min-h-screen text-black">
      <div className="flex">
        <div className="w-1/2 p-4">
          
          <InputSection
            title="First Name"
            placeholder="First Name"
            data={crewJob.first_name}
            setData={crewJob.setfirst_name}
          />
          <InputSection
            title="Last Name"
            placeholder="Last Name"
            data={crewJob.last_name}
            setData={crewJob.setlast_name}
          />
          <InputSection
            title="Email"
            placeholder="Email"
            data={crewJob.email}
            setData={crewJob.setemail}
          />
          <MultiImageExample/>
          <InputSection
            title="pdf_content"
            placeholder="pdf_content"
            data={crewJob.pdf_content}
            setData={crewJob.setpdf_content}
          />
          <InputSection
            title="JD"
            placeholder="JD"
            data={crewJob.jd}
            setData={crewJob.setjd}
          />
        </div>
        <div className="w-1/2 p-4 flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Output</h2>
            
            <button
              onClick={() => crewJob.startpdfJob()}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-sm"
              disabled={crewJob.running}
            >
              {crewJob.running ? "Running..." : "Draft email"}
            </button>
            <button
              onClick={() => crewJob.startJobHR()}
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-sm"
              disabled={crewJob.running}
            >
              {crewJob.running ? "Running..." : "Find Match"}
            </button>
          </div>
          <EmailLog email={crewJob.draft} />
          <EventLog events={crewJob.events} />
        </div>
      </div>
    </div>
  );
}

function MultiImageExample() {
  const [fileStates, setFileStates] = React.useState<FileState[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const crewJob = useCrewJob();

  const [uploadRes, setUploadRes] = React.useState<
    {
      url: string;
      filename: string;
    }[]
  >([]);
  const { edgestore } = useEdgeStore();
  const extractText = async (url:string) => {
    setIsLoading(true);

    try {
      const response = await axios.post('/api/extract-text', { url });
      crewJob.setpdf_content(response.data.text);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };



  function updateFileProgress(key: string, progress: FileState['progress']) {
    setFileStates((fileStates) => {
      const newFileStates = structuredClone(fileStates);
      const fileState = newFileStates.find(
        (fileState) => fileState.key === key,
      );
      if (fileState) {
        fileState.progress = progress;
      }
      return newFileStates;
    });
  }

  return (
    <div className="flex flex-col items-center">
      <MultiFileDropzone
        value={fileStates}
        dropzoneOptions={{
          maxFiles: 10,
          maxSize: 1024 * 1024 * 1, // 1 MB
        }}
        onFilesAdded={async (addedFiles) => {
          setFileStates([...fileStates, ...addedFiles]);
          await Promise.all(
            addedFiles.map(async (addedFileState) => {
              try {
                const res = await edgestore.myPublicFiles.upload({
                  file: addedFileState.file,
                  onProgressChange: async (progress) => {
                    updateFileProgress(addedFileState.key, progress);
                    if (progress === 100) {
                      // wait 1 second to set it to complete
                      // so that the user can see the progress bar
                      await new Promise((resolve) => setTimeout(resolve, 1000));
                      updateFileProgress(addedFileState.key, 'COMPLETE');
                    }
                  },
                });
                extractText(res.url)
                setUploadRes((uploadRes) => [
                  ...uploadRes,
                  {
                    url: res.url,
                    filename: addedFileState.file.name,
                  },
                ]);
              } catch (err) {
                updateFileProgress(addedFileState.key, 'ERROR');
              }
            }),
          );
        }}
      />
      {uploadRes.length > 0 && (
        <div className="mt-2">
          {uploadRes.map((res) => (
            <a
              key={res.url}
              className="mt-2 block underline"
              href={res.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {res.filename}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

