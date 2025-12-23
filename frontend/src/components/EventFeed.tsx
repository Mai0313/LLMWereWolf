import React, { useEffect, useRef } from 'react'
import { Card, Timeline, Badge, Empty, Switch } from 'antd'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UserDeleteOutlined,
  EyeOutlined,
  MedicineBoxOutlined,
  MessageOutlined,
  HeartOutlined
} from '@ant-design/icons'
import { useGameEvents, useAutoScroll, toggleAutoScroll } from '@store/gameStore'
import { GameEvent } from '@/types/game'

interface EventItemProps {
  event: GameEvent
  isLast: boolean
}

const getEventIcon = (eventType: string) => {
  switch (eventType) {
    case 'PLAYER_DIED': return <UserDeleteOutlined className="text-red-400" />
    case 'ROLE_ACTION': return <EyeOutlined className="text-blue-400" />
    case 'POTION_USED': return <MedicineBoxOutlined className="text-purple-400" />
    case 'PROTECTION': return <ShieldCheckOutlined className="text-green-400" />
    case 'DISCUSSION': return <MessageOutlined className="text-yellow-400" />
    case 'VOTING': return <VoteOutlined className="text-orange-400" />
    case 'LOVE_BOUND': return <HeartOutlined className="text-pink-400" />
    default: return <MessageOutlined className="text-gray-400" />
  }
}

const getEventColor = (eventType: string) => {
  switch (eventType) {
    case 'PLAYER_DIED': return 'red'
    case 'ROLE_ACTION': return 'blue'
    case 'POTION_USED': return 'purple'
    case 'PROTECTION': return 'green'
    case 'DISCUSSION': return 'gold'
    case 'VOTING': return 'orange'
    case 'LOVE_BOUND': return 'magenta'
    default: return 'gray'
  }
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const EventItem: React.FC<EventItemProps> = ({ event, isLast }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -50 }}
      transition={{ duration: 0.3 }}
    >
      <Timeline.Item
        dot={getEventIcon(event.type)}
        color={getEventColor(event.type)}
        className={`${isLast ? '' : 'mb-2'}`}
      >
        <div className="space-y-1">
          {/* 时间和阶段标识 */}
          <div className="flex items-center justify-between text-xs opacity-75">
            <span>{formatTime(event.timestamp)}</span>
            <Badge
              count={`${event.round} 轮`}
              size="small"
              className="ml-2"
            />
          </div>

          {/* 事件消息 */}
          <div className="text-sm leading-relaxed">
            {event.message}
          </div>

          {/* 额外数据展示 */}
          {event.data && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="text-xs opacity-60 mt-1 p-2 bg-gray-800 rounded"
            >
              {Object.entries(event.data).map(([key, value]) => (
                <div key={key}>
                  <span className="font-medium">{key}:</span> {String(value)}
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </Timeline.Item>
    </motion.div>
  )
}

const EventFeed: React.FC = () => {
  const events = useGameEvents()
  const autoScroll = useAutoScroll()
  const timelineRef = useRef<HTMLDivElement>(null)

  // 滚动到底部
  useEffect(() => {
    if (autoScroll && timelineRef.current) {
      const scrollToBottom = () => {
        const element = timelineRef.current
        if (element) {
          element.scrollTop = element.scrollHeight
        }
      }

      // 延迟执行，等待动画完成
      const timer = setTimeout(scrollToBottom, 100)
      return () => clearTimeout(timer)
    }
  }, [events, autoScroll])

  // 过滤事件（可选，按类型或玩家）
  const filteredEvents = events.slice(-50) // 只显示最近50个事件

  if (filteredEvents.length === 0) {
    return (
      <Card
        title="游戏事件"
        size="small"
        className="h-full"
        extra={
          <Switch
            checked={autoScroll}
            onChange={toggleAutoScroll}
            size="small"
            checkedChildren="自动"
            unCheckedChildren="手动"
          />
        }
      >
        <Empty
          description="暂无事件"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    )
  }

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <span>游戏事件 ({events.length})</span>
          <Switch
            checked={autoScroll}
            onChange={toggleAutoScroll}
            size="small"
            checkedChildren="自动"
            unCheckedChildren="手动"
          />
        </div>
      }
      size="small"
      className="h-full"
      bodyStyle={{ padding: '12px' }}
    >
      <div
        ref={timelineRef}
        className="overflow-y-auto"
        style={{ maxHeight: 'calc(100vh - 200px)' }}
      >
        <AnimatePresence>
          <Timeline mode="left" className="custom-timeline">
            {filteredEvents.map((event, index) => (
              <EventItem
                key={`${event.id}-${events.length - index}`}
                event={event}
                isLast={index === filteredEvents.length - 1}
              />
            ))}
          </Timeline>
        </AnimatePresence>
      </div>

      <style jsx>{`
        .custom-timeline .ant-timeline-item-content {
          margin-left: 40px;
        }

        .custom-timeline .ant-timeline-item-tail {
          border-left: 2px solid rgba(148, 163, 184, 0.2);
        }

        .custom-timeline .ant-timeline-item-head {
          border: 2px solid;
        }
      `}</style>
    </Card>
  )
}

export default EventFeed