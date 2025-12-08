<template>
	<div class="">
		<div class="grid md:grid-cols-[75%,25%] h-screen">
			<div class="border-r">
				<header
					class="sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between border-b overflow-hidden bg-surface-white px-3 py-2.5 sm:px-5"
				>
					<Breadcrumbs class="text-ellipsis" :items="breadcrumbs" />
					<Button
						variant="solid"
						@click="saveLesson({ showSuccessMessage: true })"
						class="mt-3 md:mt-0"
					>
						{{ __('Save') }}
					</Button>
				</header>
				<div class="py-5">
					<div class="w-5/6 mx-auto">
						<FormControl
							v-model="lesson.title"
							label="Title"
							class="mb-4"
							:required="true"
						/>
						<FormControl
							v-model="lesson.include_in_preview"
							type="checkbox"
							label="Include in Preview"
						/>
					</div>
					<div class="border-t mt-4">
						<div class="w-5/6 mx-auto pt-4">
							<div
								class="flex justify-between cursor-pointer"
								@click="
									() => {
										openInstructorEditor = !openInstructorEditor
									}
								"
							>
								<label class="block font-medium text-ink-gray-5 mb-1">
									{{ __('Instructor Notes') }}
								</label>
								<ChevronRight
									class="stroke-2 h-5 w-5 text-ink-gray-5"
									:class="{
										'rotate-90 transform duration-200': openInstructorEditor,
										'duration-200': !openInstructorEditor,
									}"
								/>
							</div>
							<div
								v-show="openInstructorEditor"
								id="instructor-notes"
								class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal py-3"
							></div>
						</div>
					</div>
					<div class="border-t mt-4">
						<div class="w-5/6 mx-auto pt-4">
							<label class="block font-medium text-ink-gray-5 mb-1">
								{{ __('Content') }}
							</label>
							<div
								id="content"
								class="ProseMirror prose prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-outline-gray-2 prose-th:border-outline-gray-2 prose-td:relative prose-th:relative prose-th:bg-surface-gray-2 prose-sm max-w-none !whitespace-normal py-3"
							></div>
						</div>
					</div>
				</div>
			</div>
				<div class="ai-sidebar h-full overflow-y-auto">
					<div class="p-4 space-y-4">
						<div class="rounded-md border p-3 bg-surface-white">
							<div class="text-sm font-semibold mb-2">{{ __('AI Assistant Index') }}</div>
							<div
								v-if="user.data?.is_moderator && assistantPaused"
								class="mb-2 text-xs bg-amber-50 text-amber-800 border border-amber-200 rounded px-2 py-1 flex items-center justify-between"
							>
								<span>{{ __('Assistant auto-paused due to proxy alerts') }}</span>
								<Button size="xs" @click="clearPause">{{ __('Clear Pause') }}</Button>
							</div>
							<div class="text-xs text-ink-gray-6 mb-2">
								{{ __('Total Chunks') }}: {{ ragSummary.data?.total_chunks || 0 }}<br />
								{{ __('Attachment Chunks') }}: {{ ragSummary.data?.by_source?.File || 0 }}<br />
								{{ __('Embedded Chunks') }}: {{ ragSummary.data?.embedded_chunks || 0 }}<br />
								{{ __('Last Run') }}:
								<span v-if="ragSummary.data?.last_run">{{ ragSummary.data.last_run.last_indexed_at }}</span>
								<span v-else>—</span>
							</div>
						<div class="w-full h-2 bg-surface-gray-2 rounded">
							<div
								class="h-2 bg-brand-600 rounded"
								:style="{ width: coveragePct + '%' }"
							></div>
						</div>
						
						<!-- Attachments Info -->
						<div class="mt-3" v-if="attachStatus.data?.length">
							<div class="text-xs font-medium text-ink-gray-7 mb-1">{{ __('Attachments') }}</div>
							<div class="space-y-1 max-h-40 overflow-auto">
								<div v-for="f in attachStatus.data" :key="f.file_url" class="flex items-center justify-between text-xs">
									<span class="truncate" :title="f.file_name">{{ f.file_name }}</span>
									<span class="text-ink-gray-6">{{ f.chunks }} {{ __('chunks') }}</span>
								</div>
							</div>
						</div>
						
						<!-- Workflow Instructions -->
						<div class="text-xs text-ink-gray-6 bg-surface-gray-1 rounded p-2 mb-2 mt-3">
							<div class="font-medium text-ink-gray-7 mb-1">{{ __('AI Workflow') }}:</div>
							<div class="space-y-0.5">
								<div>{{ __('1. 📝 Index This Lesson (Required)') }}</div>
								<div>{{ __('2. 🧠 Compute Embeddings (Optional - Requires External AI)') }}</div>
								<div>{{ __('3. 🔄 Rebuild Index (Steps 1+2 Combined)') }}</div>
								<div>{{ __('4. 🎯 Generate Quiz/FAQ/Summary (Optional - Requires AI)') }}</div>
							</div>
						</div>
						
						<div class="space-y-2">
								<Button size="sm" class="w-full justify-start" @click="indexNow">{{ __('Index This Lesson') }}</Button>
								<Button size="sm" class="w-full justify-start" @click="embedNow">{{ __('Compute Embeddings') }}</Button>
                            <Button size="sm" class="w-full justify-start" @click="rebuildNow">{{ __('Rebuild Index') }}</Button>
                            <Button size="sm" class="w-full justify-start" v-if="user.data?.is_moderator" @click="generateQuiz">{{ __('Generate Quiz (AI)') }}</Button>
                            <Button size="sm" class="w-full justify-start" v-if="user.data?.is_moderator && hasLastQuizParams" @click="regenerateQuizLast">{{ __('Regenerate Quiz (Last)') }}</Button>
                            <Button size="sm" class="w-full justify-start" v-if="user.data?.is_moderator" @click="generateDraft">{{ __('Generate Summary/Glossary') }}</Button>
                            <Button size="sm" class="w-full justify-start" v-if="user.data?.is_moderator" @click="generateFAQ">{{ __('Generate FAQ Draft') }}</Button>

							<div v-if="remainingToEmbed > 0" class="text-ink-gray-6 text-xs pt-1 break-words">
								{{ __('Remaining') }}: {{ remainingToEmbed }}
							</div>

							<div class="rounded-md border p-4 bg-surface-white mt-2">
								<div class="text-sm font-semibold mb-2">{{ __('Reports') }}</div>
								<div class="text-xs space-y-1">
									<div class="break-words">
										<a :href="'/app/query-report/AI%20Embeddings%20Coverage'" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('Open Embeddings Coverage') }}</a>
									</div>
									<div class="break-words">
										<a :href="'/app/query-report/RAG%20Index%20Runs'" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('Open Index Runs') }}</a>
									</div>
									<div class="break-words">
										<a :href="'/app/query-report/AI%20External%20Sources%20Errors'" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('Open External Errors') }}</a>
									</div>
									<div class="break-words">
										<a :href="'/app/query-report/AI%20Guardrail%20Events'" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('Open Guardrail Events') }}</a>
									</div>
								</div>
							</div>
						</div>
                        <div class="mt-1 text-xs" v-if="lastLessonDraft.data?.length || lastFaqDraft.data?.length">
                            <span class="text-ink-gray-7">{{ __('Latest Drafts') }}:</span>
                            <template v-if="lastLessonDraft.data?.length">
                                <div class="break-words">
                                    <a :href="`/app/ai-lesson-draft/${lastLessonDraft.data[0].name}`" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('Summary/Glossary') }}</a>
                                </div>
                            </template>
                            <template v-if="lastFaqDraft.data?.length">
                                <div class="break-words">
                                    <a :href="`/app/ai-faq-draft/${lastFaqDraft.data[0].name}`" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('FAQ') }}</a>
                                </div>
                            </template>
                        </div>
							<div class="rounded-md border p-4 bg-surface-white mt-2">
								<div class="text-sm font-semibold mb-2">{{ __('External Sources') }}</div>
								<div class="text-xs text-ink-gray-6 mb-2 break-words">
									{{ __('Allowed Domains') }}: {{ externalAllowedDomains || '—' }}
								</div>
								<div class="space-y-1 max-h-28 overflow-auto mb-2" v-if="lessonExternalSources.length">
									<div v-for="s in lessonExternalSources" :key="s.name" class="text-xs break-words">
										<span class="font-medium">{{ s.title || s.url }}</span>
										<span class="text-ink-gray-6"> — {{ s.status }}</span>
									</div>
								</div>
								<div class="text-xs space-y-1">
									<div class="space-y-1">
										<div class="break-words">
											<a @click.prevent="indexLessonExternalNow" class="text-brand-600 hover:underline cursor-pointer break-words">{{ __('Index External Sources') }}</a>
										</div>
										<div class="break-words">
											<a :href="'/app/ai-external-source'" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('Open External Sources') }}</a>
										</div>
										<div class="break-words">
											<a :href="newExternalHref" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('New External Source') }}</a>
										</div>
									</div>
									<div class="break-words">
										<a :href="'/app/query-report/AI%20External%20Sources%20Summary'" target="_blank" class="text-brand-600 hover:underline break-words">{{ __('Open External Summary') }}</a>
									</div>
								</div>
							</div>
							</div>
						<LessonHelp />
					</div>
				</div>
			</div>
		</div>
</template>
<script setup>
import {
    Breadcrumbs,
    Button,
    call,
    createResource,
    FormControl,
    usePageMeta,
    toast,
} from 'frappe-ui'
import {
    computed,
    reactive,
    onMounted,
    inject,
    ref,
    onBeforeUnmount,
    getCurrentInstance,
} from 'vue'
import { sessionStore } from '../stores/session'
import EditorJS from '@editorjs/editorjs'
import LessonHelp from '@/components/LessonHelp.vue'
import { ChevronRight } from 'lucide-vue-next'
import { getEditorTools, enablePlyr } from '@/utils'
import { capture, startRecording, stopRecording } from '@/telemetry'
import { useOnboarding } from 'frappe-ui/frappe'

const { brand } = sessionStore()
const editor = ref(null)
const instructorEditor = ref(null)
const user = inject('$user')
const app = getCurrentInstance()
const { $dialog } = app.appContext.config.globalProperties
const openInstructorEditor = ref(false)
const externalAllowedDomains = ref('')
const { updateOnboardingStep } = useOnboarding('learning')
let autoSaveInterval
let showSuccessMessage = false

const props = defineProps({
	courseName: {
		type: String,
		required: true,
	},
	chapterNumber: {
		type: String,
		required: true,
	},
	lessonNumber: {
		type: String,
		required: true,
	},
})

onMounted(() => {
	if (!user.data?.is_moderator && !user.data?.is_instructor) {
		window.location.href = '/login'
	}
	capture('lesson_form_opened')
	startRecording()
	editor.value = renderEditor('content')
	instructorEditor.value = renderEditor('instructor-notes')
	window.addEventListener('keydown', keyboardShortcut)
	enablePlyr()
})

const renderEditor = (holder) => {
	return new EditorJS({
		holder: holder,
		tools: getEditorTools(true),
		autofocus: true,
		defaultBlock: 'markdown',
		onChange: async (api, event) => {
			enablePlyr()
		},
	})
}

const lesson = reactive({
	title: '',
	include_in_preview: false,
	body: '',
	instructor_notes: '',
	content: '',
})

const lessonDetails = createResource({
	url: 'lms.lms.utils.get_lesson_creation_details',
	params: {
		course: props.courseName,
		chapter: props.chapterNumber,
		lesson: props.lessonNumber,
	},
	auto: true,
	onSuccess(data) {
		if (data.lesson) {
			Object.keys(data.lesson).forEach((key) => {
				lesson[key] = data.lesson[key]
			})
			lesson.include_in_preview = data?.lesson?.include_in_preview
				? true
				: false
			addLessonContent(data)
			addInstructorNotes(data)
			enableAutoSave()
		}
	},
})

const addLessonContent = (data) => {
	editor.value.isReady.then(() => {
		if (data.lesson.content) {
			editor.value.render(JSON.parse(data.lesson.content))
		} else if (data.lesson.body) {
			let blocks = convertToJSON(data.lesson)
			editor.value.render({
				blocks: blocks,
			})
		}
	})
}

const addInstructorNotes = (data) => {
	instructorEditor.value.isReady.then(() => {
		if (data.lesson.instructor_content) {
			instructorEditor.value.render(JSON.parse(data.lesson.instructor_content))
		} else if (data.lesson.instructor_notes) {
			let blocks = convertToJSON(data.lesson)
			instructorEditor.value.render({
				blocks: blocks,
			})
		}
	})
}

const enableAutoSave = () => {
	autoSaveInterval = setInterval(() => {
		saveLesson({ showSuccessMessage: false })
	}, 10000)
}

const keyboardShortcut = (e) => {
	if (
		e.key === 's' &&
		(e.ctrlKey || e.metaKey) &&
		!e.target.classList.contains('ProseMirror')
	) {
		saveLesson({ showSuccessMessage: true })
		e.preventDefault()
	}
}

onBeforeUnmount(() => {
	clearInterval(autoSaveInterval)
	window.removeEventListener('keydown', keyboardShortcut)
	stopRecording()
})

const newLessonResource = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'Course Lesson',
				course: props.courseName,
				chapter: lessonDetails.data?.chapter.name,
				...lesson,
			},
		}
	},
})

const editLesson = createResource({
	url: 'frappe.client.set_value',
	makeParams(values) {
		return {
			doctype: 'Course Lesson',
			name: values.lesson,
			fieldname: lesson,
		}
	},
})

const lessonReference = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'Lesson Reference',
				parent: lessonDetails.data?.chapter.name,
				parenttype: 'Course Chapter',
				parentfield: 'lessons',
				lesson: values.lesson,
				idx: props.lessonNumber,
			},
		}
	},
})

const convertToJSON = (lessonData) => {
	let blocks = []
	if (lessonData.youtube) {
		let youtubeID = lessonData.youtube.split('/').pop()
		blocks.push({
			type: 'embed',
			data: {
				service: 'youtube',
				embed: `https://www.youtube.com/embed/${youtubeID}`,
			},
		})
	}
	lessonData.body.split('\n').forEach((block) => {
		if (block.includes('{{ YouTubeVideo')) {
			let youtubeID = block.match(/\(["']([^"']+?)["']\)/)[1]
			if (!youtubeID.includes('https://'))
				youtubeID = `https://www.youtube.com/embed/${youtubeID}`
			blocks.push({
				type: 'embed',
				data: {
					service: 'youtube',
					embed: youtubeID,
				},
			})
		} else if (block.includes('{{ Quiz')) {
			let quiz = block.match(/\(["']([^"']+?)["']\)/)[1]
			blocks.push({
				type: 'quiz',
				data: {
					quiz: quiz,
				},
			})
		} else if (block.includes('{{ Video')) {
			let video = block.match(/\(["']([^"']+?)["']\)/)[1]
			blocks.push({
				type: 'upload',
				data: {
					file_url: video,
					file_type: video.split('.').pop(),
				},
			})
		} else if (block.includes('{{ Audio')) {
			let audio = block.match(/\(["']([^"']+?)["']\)/)[1]
			blocks.push({
				type: 'upload',
				data: {
					file_url: audio,
					file_type: audio.split('.').pop(),
				},
			})
		} else if (block.includes('{{ PDF')) {
			let pdf = block.match(/\(["']([^"']+?)["']\)/)[1]
			blocks.push({
				type: 'upload',
				data: {
					file_url: pdf,
					file_type: 'pdf',
				},
			})
		} else if (block.includes('{{ Embed')) {
			let embed = block.match(/\(["']([^"']+?)["']\)/)[1]
			blocks.push({
				type: 'embed',
				data: {
					service: embed.split('|||')[0],
					embed: embed.split('|||')[1],
				},
			})
		} else if (block.includes('![]')) {
			let image = block.match(/\((.*?)\)/)[1]
			blocks.push({
				type: 'upload',
				data: {
					file_url: image,
					file_type: 'image',
				},
			})
		} else if (block.includes('#')) {
			let level = (block.match(/#/g) || []).length
			blocks.push({
				type: 'header',
				data: {
					text: block.replace(/#/g, '').trim(),
					level: level,
				},
			})
		} else {
			blocks.push({
				type: 'paragraph',
				data: {
					text: block,
				},
			})
		}
	})

	if (lessonData.quizId) {
		blocks.push({
			type: 'quiz',
			data: {
				quiz: lessonData.quizId,
			},
		})
	}

	return blocks
}

const saveLesson = (e) => {
	showSuccessMessage = false
	if (typeof e != 'undefined' && e.showSuccessMessage) {
		showSuccessMessage = true
	}
	editor.value.save().then((outputData) => {
		outputData = removeEmptyBlocks(outputData)
		lesson.content = JSON.stringify(outputData)
		instructorEditor.value.save().then((outputData) => {
			outputData = removeEmptyBlocks(outputData)
			lesson.instructor_content = JSON.stringify(outputData)
			if (lessonDetails.data?.lesson) {
				editCurrentLesson()
			} else {
				createNewLesson()
			}
		})
	})
}

const removeEmptyBlocks = (outputData) => {
	let blocks = outputData.blocks.filter((block) => {
		return Object.keys(block.data).length > 0 || block.type == 'paragraph'
	})
	outputData.blocks = blocks
	return outputData
}

const createNewLesson = () => {
	newLessonResource.submit(
		{},
		{
			validate() {
				return validateLesson()
			},
			onSuccess(data) {
				lessonReference.submit(
					{ lesson: data.name },
					{
						onSuccess() {
							if (user.data?.is_system_manager)
								updateOnboardingStep('create_first_lesson')

							capture('lesson_created')
							toast.success(__('Lesson created successfully'))
							lessonDetails.reload()
						},
					}
				)
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const editCurrentLesson = () => {
	editLesson.submit(
		{
			lesson: lessonDetails.data.lesson.name,
		},
		{
			validate() {
				return validateLesson()
			},
			onSuccess() {
				showSuccessMessage
					? toast.success(__('Lesson updated successfully'))
					: ''
			},
			onError(err) {
				toast.error(err.message)
			},
		}
	)
}

const validateLesson = () => {
	if (!lesson.title) {
		return 'Title is required'
	}
	if (!lesson.content) {
		return 'Content is required'
	}
}

const breadcrumbs = computed(() => {
	let crumbs = [
		{
			label: 'Courses',
			route: { name: 'Courses' },
		},
		{
			label: lessonDetails.data?.course_title,
			route: { name: 'CourseForm', params: { courseName: props.courseName } },
		},
	]

	if (lessonDetails?.data?.lesson) {
		crumbs.push({
			label: lessonDetails.data.lesson.title,
			route: {
				name: 'Lesson',
				params: {
					courseName: props.courseName,
					chapterNumber: props.chapterNumber,
					lessonNumber: props.lessonNumber,
				},
			},
		})
	}
	crumbs.push({
		label: lessonDetails?.data?.lesson ? 'Edit Lesson' : 'Create Lesson',
		route: {
			name: 'LessonForm',
			params: {
				courseName: props.courseName,
				chapterNumber: props.chapterNumber,
				lessonNumber: props.lessonNumber,
			},
		},
	})
	return crumbs
})

usePageMeta(() => {
    return {
        title: lessonDetails?.data?.lesson
            ? lessonDetails.data.lesson.title
            : 'New Lesson',
        icon: brand.favicon,
    }
})
// RAG indexing summary and action for this lesson
const ragSummary = createResource({
  url: 'lms.lms.api.get_rag_index_summary',
  makeParams() {
    const lessonName = lessonDetails?.data?.lesson?.name
    return { course: props.courseName, lesson: lessonName }
  },
  auto: true,
})

const attachStatus = createResource({
  url: 'lms.lms.api.get_lesson_attachment_status',
  makeParams() {
    const lessonName = lessonDetails?.data?.lesson?.name
    return { lesson: lessonName }
  },
  auto: true,
})

// External Sources for this lesson (filter from course sources)
const externalSources = createResource({
  url: 'lms.lms.api.get_external_sources',
  makeParams() {
    return { course: props.courseName }
  },
  auto: true,
})

const lessonExternalSources = computed(() => {
  const ln = lessonDetails?.data?.lesson?.name
  const rows = externalSources.data || []
  return (rows || []).filter((r) => r.lesson === ln)
})

const newExternalHref = computed(() => {
  const ln = lessonDetails?.data?.lesson?.name || ''
  return `/app/ai-external-source/new?course=${props.courseName || ''}&lesson=${ln}`
})

const indexLessonExternalJob = createResource({
  url: 'lms.lms.api.enqueue_external_sources_lesson',
  makeParams() {
    return { course: props.courseName, lesson: lessonDetails?.data?.lesson?.name }
  },
})

const indexLessonExternalNow = async () => {
  try {
    await indexLessonExternalJob.submit()
    toast.success(__('External sources indexing started'))
  } catch (e) {
    toast.error(__('Failed to enqueue external indexing'))
  }
}

// Latest drafts (lesson)
const lastLessonDraft = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    const lessonName = lessonDetails?.data?.lesson?.name
    return {
      doctype: 'AI Lesson Draft',
      fields: ['name', 'modified'],
      filters: { lesson: lessonName },
      order_by: 'modified desc',
      limit_page_length: 1,
    }
  },
  auto: true,
})

const lastFaqDraft = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    const lessonName = lessonDetails?.data?.lesson?.name
    return {
      doctype: 'AI FAQ Draft',
      fields: ['name', 'modified'],
      filters: { lesson: lessonName },
      order_by: 'modified desc',
      limit_page_length: 1,
    }
  },
  auto: true,
})

// Assistant paused flag (moderators only) and clear action
const assistantPaused = ref(false)
const loadAssistantPaused = async () => {
  try {
    const res = await call('frappe.client.get_value', {
      doctype: 'AI Assistant Config',
      fieldname: 'paused_by_alert',
      filters: { course: props.courseName },
    })
    assistantPaused.value = !!res?.message?.paused_by_alert
  } catch (e) {
    assistantPaused.value = false
  }
}
onMounted(() => {
  loadAssistantPaused()
  loadAllowedDomains()
})

const loadAllowedDomains = async () => {
  try {
    const res = await call('frappe.client.get_value', {
      doctype: 'LMS Settings',
      fieldname: 'assistant_external_allowed_domains',
    })
    externalAllowedDomains.value = res?.message?.assistant_external_allowed_domains || ''
  } catch (e) {
    externalAllowedDomains.value = ''
  }
}

const clearPause = async () => {
  try {
    await call('lms.lms.api.clear_assistant_pause', { course: props.courseName })
    assistantPaused.value = false
    toast.success(__('Assistant unpaused'))
  } catch (e) {
    toast.error(__('Failed to clear pause'))
  }
}

const coveragePct = computed(() => {
  const t = ragSummary.data?.total_chunks || 0
  const e = ragSummary.data?.embedded_chunks || 0
  if (!t) return 0
  return Math.round((e * 100) / t)
})

const remainingToEmbed = computed(() => {
  const t = ragSummary.data?.total_chunks || 0
  const e = ragSummary.data?.embedded_chunks || 0
  const r = t - e
  return r > 0 ? r : 0
})

const indexJob = createResource({
  url: 'lms.lms.api.enqueue_rag_index_lesson',
  makeParams() {
    const lessonName = lessonDetails?.data?.lesson?.name
    return { lesson: lessonName }
  },
})

const indexNow = async () => {
  try {
    await indexJob.submit()
    toast.success(__('Indexing started'))
    toast.info(__('Track progress in Desk → Reports → AI Embeddings Coverage'))
  } catch (e) {
    toast.error(__('Failed to enqueue indexing'))
  }
}

const embedJob = createResource({
  url: 'lms.lms.api.enqueue_rag_embeddings_lesson',
  makeParams() {
    const lessonName = lessonDetails?.data?.lesson?.name
    return { lesson: lessonName }
  },
})

const embedNow = async () => {
  try {
    await embedJob.submit()
    toast.success(__('Embeddings job started'))
    toast.info(__('Track progress in Desk → Reports → AI Embeddings Coverage'))
  } catch (e) {
    toast.error(__('Failed to enqueue embeddings job'))
  }
}

const rebuildJob = createResource({
  url: 'lms.lms.api.enqueue_rag_rebuild_lesson',
  makeParams() {
    const lessonName = lessonDetails?.data?.lesson?.name
    return { lesson: lessonName }
  },
})

const rebuildNow = async () => {
  try {
    await rebuildJob.submit()
    toast.success(__('Rebuild job started'))
    toast.info(__('Track progress in Desk → Reports → AI Embeddings Coverage'))
  } catch (e) {
    toast.error(__('Failed to enqueue rebuild'))
  }
}

// AI Instructor tools
const quizJob = createResource({
  url: 'lms.lms.api.generate_quiz_from_lesson',
  makeParams(values) {
    return {
      lesson: lessonDetails?.data?.lesson?.name,
      num_questions: values?.num_questions || 6,
      difficulty: values?.difficulty || 'medium',
    }
  },
})

const generateQuiz = async () => {
  // Open a small params dialog
  const state = reactive({ num_questions: 6, difficulty: 'medium' })
  $dialog({
    title: __('Generate Quiz (AI)'),
    message: () => {
      return (
        `<div class="space-y-2 text-sm">` +
        `<div>${__('Number of Questions')}</div>` +
        `<input type="number" min="1" max="20" value="${state.num_questions}" id="ai-num-q" class="border rounded px-2 py-1 w-full" />` +
        `<div class="mt-2">${__('Difficulty')}</div>` +
        `<select id="ai-diff" class="border rounded px-2 py-1 w-full">` +
        `<option value="easy">${__('easy')}</option>` +
        `<option value="medium" selected>${__('medium')}</option>` +
        `<option value="hard">${__('hard')}</option>` +
        `</select>` +
        `</div>`
      )
    },
    actions: [
      {
        label: __('Cancel'),
      },
      {
        label: __('Generate'),
        variant: 'solid',
        onClick: async (close) => {
          try {
            const nq = parseInt((document.getElementById('ai-num-q') || {}).value || '6')
            const diff = (document.getElementById('ai-diff') || {}).value || 'medium'
            const res = await quizJob.submit({ num_questions: nq, difficulty: diff })
            if (res?.ok) {
              toast.success(__('Quiz generated'))
              window.open(`/app/lms-quiz/${res.quiz}`, '_blank')
              try {
                const key = `ai_quiz_params:${lessonDetails?.data?.lesson?.name || ''}`
                localStorage.setItem(key, JSON.stringify({ num_questions: nq, difficulty: diff }))
              } catch (e) {}
              close()
            } else {
              throw new Error('failed')
            }
          } catch (e) {
            toast.error(__('Failed to generate quiz'))
          }
        },
      },
    ],
  })
}

const hasLastQuizParams = computed(() => {
  try {
    const key = `ai_quiz_params:${lessonDetails?.data?.lesson?.name || ''}`
    return !!localStorage.getItem(key)
  } catch (e) { return false }
})

const regenerateQuizLast = async () => {
  try {
    const key = `ai_quiz_params:${lessonDetails?.data?.lesson?.name || ''}`
    const raw = localStorage.getItem(key)
    const params = raw ? JSON.parse(raw) : { num_questions: 6, difficulty: 'medium' }
    const res = await quizJob.submit(params)
    if (res?.ok) {
      toast.success(__('Quiz generated'))
      window.open(`/app/lms-quiz/${res.quiz}`, '_blank')
    } else {
      throw new Error('failed')
    }
  } catch (e) {
    toast.error(__('Failed to generate quiz'))
  }
}

const draftJob = createResource({
  url: 'lms.lms.api.generate_lesson_draft',
  makeParams() {
    return { lesson: lessonDetails?.data?.lesson?.name }
  },
})

const generateDraft = async () => {
  try {
    const res = await draftJob.submit()
    if (res?.ok) {
      toast.success(__('Draft generated'))
      window.open(`/app/ai-lesson-draft/${res.draft}`, '_blank')
    } else {
      throw new Error('failed')
    }
  } catch (e) {
    toast.error(__('Failed to generate draft'))
  }
}

const faqJob = createResource({
  url: 'lms.lms.api.generate_faq_from_transcripts',
  makeParams() {
    return { course: props.courseName, lesson: lessonDetails?.data?.lesson?.name, max_pairs: 20 }
  },
})

const generateFAQ = async () => {
  try {
    const res = await faqJob.submit()
    if (res?.ok) {
      toast.success(__('FAQ draft generated'))
      window.open(`/app/ai-faq-draft/${res.draft}`, '_blank')
    } else {
      throw new Error('failed')
    }
  } catch (e) {
    toast.error(__('Failed to generate FAQ'))
  }
}

</script>
<style>
/* AI sidebar containment and wrapping */
.ai-sidebar { min-width: 0; }
.ai-sidebar .sticky { min-width: 0; }
.ai-sidebar a { overflow-wrap: anywhere; word-break: break-word; }
.ai-sidebar button, .ai-sidebar .btn, .ai-sidebar .frappe-button {
  max-width: 100%;
  white-space: normal;
  flex-wrap: wrap;
}
.ai-sidebar .rounded-md.border, .ai-sidebar .rounded-lg.border { min-width: 0; }
.embed-tool__caption,
.cdx-simple-image__caption {
	display: none;
}

.ce-block__content {
	max-width: none;
}

.codex-editor--narrow .ce-toolbar__actions {
	right: 100%;
}

.ce-toolbar__content {
	max-width: none;
}

.codeBoxHolder {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	align-items: flex-start;
}

.codeBoxTextArea {
	width: 100%;
	min-height: 30px;
	padding: 10px;
	border-radius: 2px 2px 2px 0;
	border: none !important;
	outline: none !important;
	font: 14px monospace;
}

.codeBoxSelectDiv {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	align-items: flex-start;
	position: relative;
}

.codeBoxSelectInput {
	border-radius: 0 0 20px 2px;
	padding: 2px 26px;
	padding-top: 0;
	padding-right: 0;
	text-align: left;
	cursor: pointer;
	border: none !important;
	outline: none !important;
}

.codeBoxSelectDropIcon {
	position: absolute !important;
	left: 10px !important;
	bottom: 0 !important;
	width: unset !important;
	height: unset !important;
	font-size: 16px !important;
}

.codeBoxSelectPreview {
	display: none;
	flex-direction: column;
	justify-content: flex-start;
	align-items: flex-start;
	border-radius: 2px;
	box-shadow: 0 3px 15px -3px rgba(13, 20, 33, 0.13);
	position: absolute;
	top: 100%;
	margin: 5px 0;
	max-height: 30vh;
	overflow-x: hidden;
	overflow-y: auto;
	z-index: 10000;
}

.codeBoxSelectItem {
	width: 100%;
	padding: 5px 20px;
	margin: 0;
	cursor: pointer;
}

.codeBoxSelectedItem {
	background-color: lightblue !important;
}

.codeBoxShow {
	display: flex !important;
}

.dark {
	color: #abb2bf;
	background-color: #282c34;
}

.light {
	color: #383a42;
	background-color: #fafafa;
}

.codeBoxTextArea {
	line-height: 1.7;
}

.prose :where(pre):not(:where([class~='not-prose'], [class~='not-prose'] *)) {
	overflow-x: unset;
}

iframe {
	border: none !important;
}

.tc-table {
	border-left: 1px solid #e8e8eb;
}

.ce-toolbox__button[data-tool='markdown'] {
	display: none !important;
}

.ce-popover-item[data-item-name='markdown'] {
	display: none !important;
}

.plyr__volume input[type='range'] {
	display: none;
}

.plyr__control--overlaid {
	background: radial-gradient(
		circle,
		rgba(0, 0, 0, 0.4) 0%,
		rgba(0, 0, 0, 0.5) 50%
	);
}

.plyr__control:hover {
	background: none;
}

.plyr--video {
	border: 1px solid theme('colors.gray.200');
	border-radius: 8px;
}

.ce-popover__container {
	border-radius: 12px;
	padding: 8px;
}

.cdx-search-field {
	border: none;
}

.cdx-search-field__input {
	font-weight: 400;
	font-size: 13px;
}

.cdx-search-field__input::before {
	font-weight: 400;
}

.cdx-search-field__input:focus {
	--tw-ring-color: theme('colors.gray.100');
}

.ce-popover-item__title {
	font-size: 13px;
	font-weight: 400;
}

.ce-popover-item__icon svg {
	width: 15px;
	height: 15px;
}

.ce-popover--opened > .ce-popover__container {
	max-height: unset;
}

.cdx-search-field__icon svg {
	width: 15px;
	height: 15px;
}

.cdx-search-field__icon {
	margin-right: 5px;
}

.cdx-block.embed-tool {
	position: relative;
	display: inline-block;
	width: 100%;
}

:root {
	--plyr-range-fill-background: white;
	--plyr-video-control-background-hover: transparent;
}

/* Keep AI sidebar content properly scrollable and wrapped */
.ai-sidebar {
  min-width: 0;
}
.ai-sidebar a {
  overflow-wrap: anywhere;
  word-break: break-word;
}
.ai-sidebar button,
.ai-sidebar .btn,
.ai-sidebar .frappe-button {
  max-width: 100%;
  white-space: normal;
  flex-wrap: wrap;
}
.ai-sidebar .rounded-md.border {
  min-width: 0;
}
</style>
