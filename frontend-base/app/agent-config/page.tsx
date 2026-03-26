'use client'

import { useState, useEffect } from 'react'
import { Loader2, Save, RefreshCw, Bot } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DashboardShell } from '@/components/dashboard-shell'

const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000'

interface AgentConfig {
  role: string
  goal: string
  backstory: string
  memory: boolean
  max_iter: number
}

interface TaskConfig {
  description: string
  expected_output: string
  agent: string
}

interface KnowledgeFile {
  name: string
  content: string
}

export default function AgentConfigPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [reloading, setReloading] = useState(false)
  
  // Agent config
  const [agentName, setAgentName] = useState('sales_consultant')
  const [agentConfig, setAgentConfig] = useState<AgentConfig>({
    role: '',
    goal: '',
    backstory: '',
    memory: false,
    max_iter: 10
  })
  
  // Task config
  const [taskName, setTaskName] = useState('sales_consult_task')
  const [taskConfig, setTaskConfig] = useState<TaskConfig>({
    description: '',
    expected_output: '',
    agent: 'sales_consultant'
  })

  // Knowledge files
  const [knowledgeFiles, setKnowledgeFiles] = useState<string[]>([])
  const [selectedKnowledge, setSelectedKnowledge] = useState<string>('')
  const [knowledgeContent, setKnowledgeContent] = useState<string>('')

  useEffect(() => {
    loadConfigs()
  }, [])

  const checkApiConnection = async () => {
    try {
      const res = await fetch(`${AGENT_API_URL}/health`)
      if (res.ok) {
        console.log('Agent API connected successfully')
      } else {
        console.error('Agent API returned error:', res.status)
      }
    } catch (error) {
      console.error('Cannot connect to Agent API:', error)
      alert('Không thể kết nối tới Agent API. Vui lòng kiểm tra:\n1. Agent API có đang chạy không?\n2. URL có đúng không? (' + AGENT_API_URL + ')')
    }
  }

  useEffect(() => {
    checkApiConnection()
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    setLoading(true)
    try {
      // Load agents
      const agentsRes = await fetch(`${AGENT_API_URL}/config/agents`)
      const agentsData = await agentsRes.json()
      
      if (agentsData.agents && agentsData.agents[agentName]) {
        setAgentConfig(agentsData.agents[agentName])
      }
      
      // Load tasks
      const tasksRes = await fetch(`${AGENT_API_URL}/config/tasks`)
      const tasksData = await tasksRes.json()
      
      if (tasksData.tasks && tasksData.tasks[taskName]) {
        setTaskConfig(tasksData.tasks[taskName])
      }

      // Load knowledge files list
      const knowledgeRes = await fetch(`${AGENT_API_URL}/knowledge/files`)
      const knowledgeData = await knowledgeRes.json()
      
      if (knowledgeData.files) {
        setKnowledgeFiles(knowledgeData.files)
        if (knowledgeData.files.length > 0 && !selectedKnowledge) {
          setSelectedKnowledge(knowledgeData.files[0])
          loadKnowledgeFile(knowledgeData.files[0])
        }
      }
    } catch (error) {
      console.error('Error loading configs:', error)
      alert('Lỗi khi tải cấu hình. Kiểm tra Agent API đang chạy.')
    } finally {
      setLoading(false)
    }
  }

  const loadKnowledgeFile = async (filename: string) => {
    try {
      const res = await fetch(`${AGENT_API_URL}/knowledge/files/${filename}`)
      const data = await res.json()
      
      if (data.content) {
        setKnowledgeContent(data.content)
      }
    } catch (error) {
      console.error('Error loading knowledge file:', error)
      alert('Lỗi khi tải file knowledge')
    }
  }

  const saveAgentConfig = async () => {
    setSaving(true)
    try {
      const res = await fetch(`${AGENT_API_URL}/config/agents/${agentName}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agentConfig)
      })
      
      if (!res.ok) throw new Error('Failed to save agent config')
      
      alert('Đã lưu cấu hình agent thành công!')
    } catch (error) {
      console.error('Error saving agent config:', error)
      alert('Lỗi khi lưu cấu hình agent')
    } finally {
      setSaving(false)
    }
  }

  const saveTaskConfig = async () => {
    setSaving(true)
    try {
      const res = await fetch(`${AGENT_API_URL}/config/tasks/${taskName}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskConfig)
      })
      
      if (!res.ok) throw new Error('Failed to save task config')
      
      alert('Đã lưu cấu hình task thành công!')
    } catch (error) {
      console.error('Error saving task config:', error)
      alert('Lỗi khi lưu cấu hình task')
    } finally {
      setSaving(false)
    }
  }

  const saveKnowledgeFile = async () => {
    if (!selectedKnowledge) {
      alert('Vui lòng chọn file knowledge')
      return
    }

    setSaving(true)
    try {
      const res = await fetch(`${AGENT_API_URL}/knowledge/files/${selectedKnowledge}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: knowledgeContent })
      })
      
      if (!res.ok) throw new Error('Failed to save knowledge file')
      
      alert('Đã lưu file knowledge thành công!')
    } catch (error) {
      console.error('Error saving knowledge file:', error)
      alert('Lỗi khi lưu file knowledge')
    } finally {
      setSaving(false)
    }
  }

  const reloadConfig = async () => {
    setReloading(true)
    try {
      const res = await fetch(`${AGENT_API_URL}/config/reload`, {
        method: 'POST'
      })
      
      if (!res.ok) throw new Error('Failed to reload config')
      
      alert('Đã reload cấu hình thành công! Agent sẽ sử dụng config mới.')
    } catch (error) {
      console.error('Error reloading config:', error)
      alert('Lỗi khi reload cấu hình')
    } finally {
      setReloading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <DashboardShell>
      <div className="flex-1 flex flex-col bg-background">
        <div className="px-8 py-6 border-b border-border">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold text-foreground flex items-center gap-2">
                <Bot className="w-8 h-8" />
                Quản lý Agent
              </h2>
              <p className="text-muted-foreground text-sm mt-1">
                Cấu hình agent và task cho hệ thống tư vấn
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={loadConfigs} variant="outline" className="gap-2">
                <RefreshCw className="w-4 h-4" />
                Tải lại
              </Button>
              <Button onClick={reloadConfig} disabled={reloading} className="gap-2">
                {reloading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
                Reload Agent
              </Button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-8 py-6">
          <Tabs defaultValue="agent" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="agent">Agent Config</TabsTrigger>
              <TabsTrigger value="task">Task Config</TabsTrigger>
              <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
            </TabsList>

            <TabsContent value="agent">
              <Card>
                <CardHeader>
                  <CardTitle>Cấu hình Agent: {agentName}</CardTitle>
                  <CardDescription>
                    Chỉnh sửa role, goal, backstory của agent
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Textarea
                      id="role"
                      value={agentConfig.role}
                      onChange={(e) => setAgentConfig({ ...agentConfig, role: e.target.value })}
                      className="min-h-[80px] [field-sizing:initial] whitespace-pre-wrap"
                      placeholder="Vai trò của agent..."
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="goal">Goal</Label>
                    <Textarea
                      id="goal"
                      value={agentConfig.goal}
                      onChange={(e) => setAgentConfig({ ...agentConfig, goal: e.target.value })}
                      className="min-h-[120px] [field-sizing:initial] whitespace-pre-wrap"
                      placeholder="Mục tiêu của agent..."
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="backstory">Backstory</Label>
                    <Textarea
                      id="backstory"
                      value={agentConfig.backstory}
                      onChange={(e) => setAgentConfig({ ...agentConfig, backstory: e.target.value })}
                      className="min-h-[120px] [field-sizing:initial] whitespace-pre-wrap"
                      placeholder="Bối cảnh của agent..."
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="max_iter">Max Iterations</Label>
                      <Input
                        id="max_iter"
                        type="number"
                        value={agentConfig.max_iter}
                        onChange={(e) => setAgentConfig({ ...agentConfig, max_iter: parseInt(e.target.value) })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="memory">Memory</Label>
                      <select
                        id="memory"
                        value={agentConfig.memory ? 'true' : 'false'}
                        onChange={(e) => setAgentConfig({ ...agentConfig, memory: e.target.value === 'true' })}
                        className="w-full h-10 px-3 rounded-md border border-input bg-background"
                      >
                        <option value="false">False</option>
                        <option value="true">True</option>
                      </select>
                    </div>
                  </div>

                  <Button onClick={saveAgentConfig} disabled={saving} className="w-full gap-2">
                    {saving ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Save className="w-4 h-4" />
                    )}
                    Lưu Agent Config
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="task">
              <Card>
                <CardHeader>
                  <CardTitle>Cấu hình Task: {taskName}</CardTitle>
                  <CardDescription>
                    Chỉnh sửa description và expected output của task
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={taskConfig.description}
                      onChange={(e) => setTaskConfig({ ...taskConfig, description: e.target.value })}
                      className="min-h-[300px] [field-sizing:initial] text-sm whitespace-pre-wrap"
                      placeholder="Mô tả task..."
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="expected_output">Expected Output</Label>
                    <Textarea
                      id="expected_output"
                      value={taskConfig.expected_output}
                      onChange={(e) => setTaskConfig({ ...taskConfig, expected_output: e.target.value })}
                      className="min-h-[120px] [field-sizing:initial] whitespace-pre-wrap"
                      placeholder="Kết quả mong đợi..."
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="agent">Agent</Label>
                    <Input
                      id="agent"
                      value={taskConfig.agent}
                      onChange={(e) => setTaskConfig({ ...taskConfig, agent: e.target.value })}
                      placeholder="Tên agent thực hiện task..."
                    />
                  </div>

                  <Button onClick={saveTaskConfig} disabled={saving} className="w-full gap-2">
                    {saving ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Save className="w-4 h-4" />
                    )}
                    Lưu Task Config
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="knowledge">
              <Card>
                <CardHeader>
                  <CardTitle>Quản lý Knowledge Files</CardTitle>
                  <CardDescription>
                    Chỉnh sửa các file kiến thức cho agent
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="knowledge-file">Chọn file</Label>
                    <select
                      id="knowledge-file"
                      value={selectedKnowledge}
                      onChange={(e) => {
                        setSelectedKnowledge(e.target.value)
                        loadKnowledgeFile(e.target.value)
                      }}
                      className="w-full h-10 px-3 rounded-md border border-input bg-background"
                    >
                      {knowledgeFiles.map((file) => (
                        <option key={file} value={file}>
                          {file}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="knowledge-content">Nội dung</Label>
                    <Textarea
                      id="knowledge-content"
                      value={knowledgeContent}
                      onChange={(e) => setKnowledgeContent(e.target.value)}
                      className="min-h-[500px] text-sm whitespace-pre-wrap break-words overflow-y-auto resize-y"
                      style={{
                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                        wordBreak: 'break-word',
                        overflowWrap: 'break-word',
                        whiteSpace: 'pre-wrap',
                        lineHeight: '1.6'
                      }}
                      placeholder="Nội dung file knowledge..."
                    />
                  </div>

                  <Button onClick={saveKnowledgeFile} disabled={saving} className="w-full gap-2">
                    {saving ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Save className="w-4 h-4" />
                    )}
                    Lưu Knowledge File
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </DashboardShell>
  )
}
