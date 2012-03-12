#pragma once

#include "../libafanasy/blockdata.h"
#include "../libafanasy/name_af.h"

#include "useraf.h"

class MonitorContainer;
class RenderAf;
class RenderContainer;
class Task;

class Block
{
public:
   Block( JobAf * blockJob, af::BlockData * blockData, af::JobProgress * progress, std::list<std::string> * log);
   virtual ~Block();

   inline bool isInitialized() const { return initialized;}

   inline void setUser( UserAf * jobOwner) { user = jobOwner;}

   inline int getErrorsAvoidHost() const
      { return ( data->getErrorsAvoidHost() > -1) ? data->getErrorsAvoidHost() : user->getErrorsAvoidHost();}
   inline int getErrorsRetries() const
      { return ( data->getErrorsRetries() > -1) ? data->getErrorsRetries() : user->getErrorsRetries();}
   inline int getErrorsTaskSameHost() const
      { return ( data->getErrorsTaskSameHost() > -1) ? data->getErrorsTaskSameHost() : user->getErrorsTaskSameHost();}
   inline int getErrorsForgiveTime() const
      { return ( data->getErrorsForgiveTime() > -1) ? data->getErrorsForgiveTime() : user->getErrorsForgiveTime();}

   int calcWeight() const;
   int logsWeight() const;
   int blackListWeight() const;

   virtual void errorHostsAppend( int task, int hostId, RenderContainer * renders);
   bool avoidHostsCheck( const std::string & hostname) const;
   virtual void getErrorHostsListString( std::string & str) const;
   virtual void errorHostsReset();

   bool canRun( RenderAf * render);

   virtual void startTask( af::TaskExec * taskexec, RenderAf * render, MonitorContainer * monitoring);

   void taskFinished( af::TaskExec * taskexec, RenderAf * render, MonitorContainer * monitoring);

   /// Refresh block. Retrun true if block progress changed, needed for jobs monitoring (watch jobs list).
   virtual bool refresh( time_t currentTime, RenderContainer * renders, MonitorContainer * monitoring);

   uint32_t action( const af::MCGeneral & mcgeneral, int type, AfContainer * pointer, MonitorContainer * monitoring);

   bool tasksDependsOn( int block);

public:
   JobAf * job;
   af::BlockData * data;
   Task ** tasks;                 ///< Tasks.
   UserAf * user;

protected:
   void appendJobLog( const std::string & message);
   bool errorHostsAppend( const std::string & hostname);

private:
   af::JobProgress * jobprogress;
   std::list<std::string> * joblog;

   std::list<std::string>  errorHosts;       ///< Avoid error hosts list.
   std::list<int>          errorHostsCounts; ///< Number of errors on error host.
   std::list<time_t>       errorHostsTime;   ///< Time of the last error

   std::list<RenderAf*> renders_ptrs;
   std::list<int> renders_counts;

   std::list<int> m_dependBlocks;
   std::list<int> m_dependTasksBlocks;
   bool initialized;             ///< Where the block was successfully  initialized.

private:
   void constructDependBlocks();

   void addRenderCounts( RenderAf * render);
   int  getRenderCounts( RenderAf * render) const;
   void remRenderCounts( RenderAf * render);
};