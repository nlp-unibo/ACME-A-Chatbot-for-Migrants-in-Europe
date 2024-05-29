import os
import tarfile
import gzip, math
import zipfile
import io
from sentence_transformers import SentenceTransformer, models, losses, evaluation
from sentence_transformers.util import http_get
from sentence_transformers.datasets import ParallelSentencesDataset
from torch.utils.data import DataLoader
from datetime import datetime
from torch.cuda import memory_summary, memory_allocated

class SentenceTranslationEmbedding:

    def __init__(self, max_sentences=20000, frac_dev_sentences=0.1, max_seq_length=128, train_batch_size=32, inference_batch_size=32, 
        source_languages=set(['eng']), target_languages=set(['deu', 'ara', 'tur', 'spa', 'ita', 'fra'])) -> None:
        
        self.source_languages = source_languages
        self.target_languages = target_languages
        self.MAX_SENTENCES = max_sentences
        self.frac_dev_sentences = frac_dev_sentences

        self.max_seq_length = max_seq_length
        self.train_batch_size = train_batch_size
        self.inference_batch_size = inference_batch_size

        # cuda0 = device("cuda:0" if cuda.is_available() else "cpu")


    def download_tatoeba_dataset(self, output_folder='parallel-sentences/'):
        
        dataset_folder = 'datasets/tatoeba'
        current_module_path = os.path.dirname(os.path.realpath(__file__))

        sentences_file_bz2 = os.path.join(current_module_path, dataset_folder, 'sentences.tar.bz2')
        links_file_bz2 = os.path.join(current_module_path, dataset_folder, 'links.tar.bz2')
        
        download_url = "https://downloads.tatoeba.org/exports/"

        if not os.path.exists(os.path.join(current_module_path, dataset_folder)):
            os.makedirs(os.path.join(current_module_path, dataset_folder))
        if not os.path.exists(os.path.join(current_module_path, output_folder)):
            os.makedirs(os.path.join(current_module_path, output_folder))

        #Download files if needed
        for filepath in [sentences_file_bz2, links_file_bz2]:
            if not os.path.exists(filepath):
                url = download_url+os.path.basename(filepath)
                print("Download", url)
                http_get(url, filepath)
        
        sentences_file = os.path.join(current_module_path, dataset_folder, 'sentences.csv')
        links_file = os.path.join(current_module_path, dataset_folder, 'links.csv')

        #Extract files if needed
        if not os.path.exists(sentences_file):
            print("Extract", sentences_file_bz2)
            tar = tarfile.open(sentences_file_bz2, "r:bz2")
            tar.extract('sentences.csv', path=os.path.join(current_module_path, dataset_folder))
            tar.close()

        if not os.path.exists(links_file):
            print("Extract", links_file_bz2)
            tar = tarfile.open(links_file_bz2, "r:bz2")
            tar.extract('links.csv', path=os.path.join(current_module_path, dataset_folder))
            tar.close()

        return sentences_file, links_file

    def prepare_tatoeba_dataset(self, sentences_file, links_file, output_folder='parallel-sentences/'):
        #Read sentences
        sentences = {}
        all_langs = self.target_languages.union(self.source_languages)
        print("Read sentences.csv file")
        with open(sentences_file, encoding='utf8') as fIn:
            for line in fIn:
                id, lang, sentence = line.strip().split('\t')
                if lang in all_langs:
                    sentences[id] = (lang, sentence)

        #Read links that map the translations between different languages
        print("Read links.csv")
        translations = {src_lang: {trg_lang: {} for trg_lang in self.target_languages} for src_lang in self.source_languages}
        with open(links_file, encoding='utf8') as fIn:
            for line in fIn:
                src_id, target_id = line.strip().split()

                if src_id in sentences and target_id in sentences:
                    src_lang, src_sent = sentences[src_id]
                    trg_lang, trg_sent = sentences[target_id]

                    if src_lang in self.source_languages and trg_lang in self.target_languages:
                        if src_sent not in translations[src_lang][trg_lang]:
                            translations[src_lang][trg_lang][src_sent] = []
                        translations[src_lang][trg_lang][src_sent].append(trg_sent)

        
        print("Write output files")
        train_files = []
        dev_files = []
        current_module_path = os.path.dirname(os.path.realpath(__file__))
        for src_lang in self.source_languages:
            for trg_lang in self.target_languages:
                source_sentences = list(translations[src_lang][trg_lang])
                source_sentences = source_sentences[:self.MAX_SENTENCES]
                n_sentences = len(source_sentences)
                n_dev_sentences = math.floor(self.frac_dev_sentences * n_sentences)
                # n_train_sentences = n_sentences - n_dev_sentences - n_test_sentences
                

                train_sentences = source_sentences[:-n_dev_sentences]
                dev_sentences = source_sentences[-n_dev_sentences:]
                # test_sentences = source_sentences[n_train_sentences+n_dev_sentences:]

                print("{}-{} has {} sentences".format(src_lang, trg_lang, n_sentences))
                if len(dev_sentences) > 0:
                    dev_file_path = os.path.join(current_module_path, output_folder, 'Tatoeba-{}-{}-dev.tsv.gz'.format(src_lang, trg_lang))
                    dev_files.append(dev_file_path)
                    with gzip.open(dev_file_path, 'wt', encoding='utf8') as fOut:
                        for sent in dev_sentences:
                            fOut.write("\t".join([sent]+translations[src_lang][trg_lang][sent]))
                            fOut.write("\n")

                if len(train_sentences) > 0:
                    train_file_path = os.path.join(current_module_path, output_folder, 'Tatoeba-{}-{}-train.tsv.gz'.format(src_lang, trg_lang))
                    train_files.append(train_file_path)
                    with gzip.open(train_file_path, 'wt', encoding='utf8') as fOut:
                        for sent in train_sentences:
                            fOut.write("\t".join([sent]+translations[src_lang][trg_lang][sent]))
                            fOut.write("\n")
        
        return train_files, dev_files

    def download_sts_dataset(self, sts_corpus='datasets/STS2017-extended.zip'):
        sts_output_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), sts_corpus)
        sts_url = "https://sbert.net/" + sts_corpus # semantic textual similarity dataset for testing
        if not os.path.exists(sts_output_folder):
            print("Download", sts_url)
            http_get(sts_url, sts_output_folder)

        return sts_output_folder

    def prepare_sts_dataset(self, sts_file):
        #Open the ZIP File of STS2017-extended.zip and check for which language combinations we have STS data\
        # sts uses 2 character language codes
        all_languages = list(map(lambda lang : lang[:-1], set(list(self.source_languages)+list(self.target_languages))))
        sts_data = {}
        with zipfile.ZipFile(sts_file) as zip:
            filelist = zip.namelist()

            for i in range(len(all_languages)):
                for j in range(i, len(all_languages)):
                    lang1 = all_languages[i]
                    lang2 = all_languages[j]
                    filepath = 'STS2017-extended/STS.{}-{}.txt'.format(lang1, lang2)
                    if filepath not in filelist:
                        lang1, lang2 = lang2, lang1
                        filepath = 'STS2017-extended/STS.{}-{}.txt'.format(lang1, lang2)

                    if filepath in filelist:
                        filename = os.path.basename(filepath)
                        sts_data[filename] = {'sentences1': [], 'sentences2': [], 'scores': []}

                        fIn = zip.open(filepath)
                        for line in io.TextIOWrapper(fIn, 'utf8'):
                            sent1, sent2, score = line.strip().split("\t")
                            score = float(score)
                            sts_data[filename]['sentences1'].append(sent1)
                            sts_data[filename]['sentences2'].append(sent2)
                            sts_data[filename]['scores'].append(score)

        return sts_data


    def prepare_teacher_student_model(self, teacher_model_name='sentence-transformers/all-mpnet-base-v2', student_model_name="sentence-transformers/paraphrase-albert-small-v2"):
        
        # Load teacher model
        print("Load teacher model")
        teacher_model = SentenceTransformer(teacher_model_name, device='cuda')

        # Create student model
        print("Create student model")
        word_embedding_model = models.Transformer(student_model_name)

        # Apply mean pooling to get one fixed sized sentence vector
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),
                                    pooling_mode_mean_tokens=True,
                                    pooling_mode_cls_token=False,
                                    pooling_mode_max_tokens=False)
        # load student model
        student_model = SentenceTransformer(modules=[word_embedding_model, pooling_model], device='cuda')

        return student_model, teacher_model

    
    def load_train_dataset(self, student_model, teacher_model, train_files):
        train_reader = ParallelSentencesDataset(student_model=student_model, teacher_model=teacher_model)


        for train_file in train_files:

            train_reader.load_data(train_file)

        train_dataloader = DataLoader(train_reader, shuffle=True, batch_size=self.train_batch_size)
        train_loss = losses.MSELoss(model=student_model)
        return train_dataloader, train_loss

    def load_evaluators(self, student_model, teacher_model, dev_files, sts_data):

        evaluators = []
        dev_reader = ParallelSentencesDataset(student_model=student_model, teacher_model=teacher_model)
        for dev_file in dev_files:
            # logger.info("Create evaluator for " + dev_file)
            dev_reader.load_data(dev_file)

            src_sentences = []
            trg_sentences = []
            with gzip.open(dev_file, 'rt', encoding='utf8') as fIn:
                for line in fIn:
                    splits = line.strip().split('\t')
                    if splits[0] != "" and splits[1] != "":
                        src_sentences.append(splits[0])
                        trg_sentences.append(splits[1])
            
            dev_mse = evaluation.MSEEvaluator(src_sentences, trg_sentences, name=os.path.basename(dev_file), teacher_model=teacher_model, batch_size=self.train_batch_size)
            evaluators.append(dev_mse)

        for filename, data in sts_data.items():
            test_evaluator = evaluation.EmbeddingSimilarityEvaluator(data['sentences1'], data['sentences2'], data['scores'], 
                batch_size=self.inference_batch_size, name=filename, show_progress_bar=False)
            evaluators.append(test_evaluator)


        return evaluators

    def fit(self, student_model, train_dataloader, train_loss, evaluators, 
        epochs=20, evaluation_steps=1000, warmup_steps=10000,
        scheduler='warmupconstant', optimizer_params={'lr':2e-5, 'eps':1e-6}):

        output_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "model", datetime.now().strftime("%Y-%m-%d"))

        # this hack is meant to avoid out of memory error
        # but might degrade training speed significantly
        # os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128" 
        print(memory_summary())
        student_model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            evaluator=evaluation.SequentialEvaluator(evaluators, main_score_function=lambda scores: scores[-1]),
            epochs=epochs,
            evaluation_steps=evaluation_steps,
            warmup_steps=warmup_steps,
            scheduler=scheduler,
            output_path=output_path,
            save_best_model=True,
            optimizer_params=optimizer_params)