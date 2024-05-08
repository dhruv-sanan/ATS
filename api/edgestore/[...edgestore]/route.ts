import { initEdgeStore } from '@edgestore/server';
import { createEdgeStoreNextHandler } from '@edgestore/server/adapters/next/app';
import { CreateContextOptions } from 'vm';


type Context = {
  userId: string;
  userRole: "admin" | "user"
}

// function createContext({ req }: CreateContextOptions): Context {
//   return{
//     userId: "123",
//     userRole: "admin"
//   }
// }
// const es = initEdgeStore.create<Context>();
const es = initEdgeStore.create();

/**
 * This is the main router for the edgestore buckets.
 */
const edgeStoreRouter = es.router({
  /**
   * A public image bucket with no validation.
   */
  myPublicImages: es.imageBucket({
    maxSize: 1024 * 1024 * 4,
  }),

  /**
   * This accepts any file type.
   */
  myPublicFiles: es.fileBucket({
    maxSize: 1024 * 1024 * 4,
  }),
  
  // myProtectedFiles: es.fileBucket({
  //   maxSize: 1024 * 1024 * 4,
  // })
  // .path(({ ctx }) => [{owner: ctx.userId}])
  // .accessControl ({
  //   OR: [
  //     {
  //       userId: {path:"owner"},
  //     },
  //     {
  //       userRole: {eq: "admin"},
  //     }
  //   ]
  // }),
});

/**
 * This is used to create the type-safe client for the frontend.
 */
export type EdgeStoreRouter = typeof edgeStoreRouter;

/**
 * The next handler is used to create the API route.
 */
const handler = createEdgeStoreNextHandler({
  router: edgeStoreRouter,
  // createContext,
});

export { handler as GET, handler as POST };